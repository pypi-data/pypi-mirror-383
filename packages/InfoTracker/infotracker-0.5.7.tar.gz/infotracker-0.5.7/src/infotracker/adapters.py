from __future__ import annotations
import json
import logging
from typing import Protocol, Dict, Any, Optional
from .parser import SqlParser
from .lineage import OpenLineageGenerator

logger = logging.getLogger(__name__)

class Adapter(Protocol):
    name: str
    dialect: str
    def extract_lineage(self, sql: str, object_hint: Optional[str] = None) -> str: ...

class MssqlAdapter:
    name = "mssql"
    dialect = "tsql"

    def __init__(self, config=None):
        self.parser = SqlParser(dialect=self.dialect)
        # Use namespace from config if available
        namespace = "mssql://localhost/InfoTrackerDW"  # default
        if config and hasattr(config, 'openlineage'):
            namespace = f"{config.openlineage.namespace}://localhost/InfoTrackerDW"
        if config and hasattr(config, 'default_database'):
            self.parser.set_default_database(config.default_database)
        if config and hasattr(config, 'default_schema'):
            try:
                self.parser.set_default_schema(config.default_schema)
            except Exception:
                pass
        # Enable dbt mode if requested
        try:
            if getattr(config, 'dbt_mode', False):
                self.parser.enable_dbt_mode(True)
        except Exception:
            pass
        self.lineage_generator = OpenLineageGenerator(namespace=namespace)

    def extract_lineage(self, sql: str, object_hint: Optional[str] = None) -> str:
        """Extract lineage from SQL and return OpenLineage JSON as string."""
        try:
            obj_info = self.parser.parse_sql_file(sql, object_hint)
            # In dbt mode, reflect a dbt-like job path; otherwise keep warehouse/sql
            job_name = None
            try:
                if getattr(self.parser, 'dbt_mode', False):
                    job_name = f"dbt/models/{object_hint}.sql" if object_hint else None
                else:
                    job_name = f"warehouse/sql/{object_hint}.sql" if object_hint else None
            except Exception:
                job_name = f"warehouse/sql/{object_hint}.sql" if object_hint else None
            json_str = self.lineage_generator.generate(
                obj_info, job_name=job_name, object_hint=object_hint
            )
            return json_str
        except Exception as exc:
            logger.error(f"Failed to extract lineage from SQL: {exc}")
            error_payload = {
                "eventType": "COMPLETE",
                "eventTime": "2025-01-01T00:00:00Z",
                "run": {"runId": "00000000-0000-0000-0000-000000000000"},
                "job": {"namespace": "infotracker/examples",
                        "name": f"warehouse/sql/{(object_hint or 'unknown')}.sql"},
                "inputs": [],
                "outputs": [{
                    "namespace": "mssql://localhost/InfoTrackerDW",
                    "name": object_hint or "unknown",
                    "facets": {
                        "schema": {
                            "_producer": "https://github.com/OpenLineage/OpenLineage",
                            "_schemaURL": "https://openlineage.io/spec/facets/1-0-0/SchemaDatasetFacet.json",
                            "fields": [
                                {"name": "error", "type": "string", "description": f"Error: {exc}"}
                            ],
                        }
                    },
                }],
            }
            return json.dumps(error_payload, indent=2, ensure_ascii=False)
        
_ADAPTERS: Dict[str, Adapter] = {}


def get_adapter(name: str, config=None) -> Adapter:
    """Return adapter keyed by dialect + important config flags.

    We include dbt_mode/defaults in the cache key to avoid reusing a parser
    configured for non-dbt runs in dbt runs (and vice versa).
    """
    # Build cache key
    try:
        dbt_flag = getattr(config, 'dbt_mode', False)
        def_db = getattr(config, 'default_database', None)
        def_sch = getattr(config, 'default_schema', None)
        key = f"{name}|dbt={dbt_flag}|db={def_db}|sch={def_sch}"
    except Exception:
        key = name
    if key not in _ADAPTERS:
        if name == "mssql":
            _ADAPTERS[key] = MssqlAdapter(config)
        else:
            raise KeyError(f"Unknown adapter '{name}'. Available: mssql")
    return _ADAPTERS[key]
