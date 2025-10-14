from sqlalchemy import text
from sqlalchemy.engine import Connection

from sqlalchemy_declarative_extensions.dialects.sqlite.schema import views_query
from sqlalchemy_declarative_extensions.view.base import View


def get_schemas_sqlite(connection: Connection):
    from sqlalchemy_declarative_extensions.schema.base import Schema

    schemas = connection.execute(text("PRAGMA database_list")).fetchall()
    return {
        schema: Schema(schema) for _, schema, *_ in schemas if schema not in {"main"}
    }


def check_schema_exists_sqlite(connection: Connection, name: str) -> bool:
    """Check whether the given schema exists.

    For `sqlalchemy.schema.CreateSchema` to work, we need to first attach
    a :memory: as the given schema name first. Given that they need to be
    created anew for each new connection, we can (hopefully) safely,
    unconditionally attach it and return `False` always.
    """
    schema_exists = "ATTACH DATABASE ':memory:' AS :schema"
    connection.execute(text(schema_exists), {"schema": name})
    return False


def get_views_sqlite(connection: Connection):
    schemas = get_schemas_sqlite(connection)
    return [
        View(v.name, v.definition, schema=v.schema)
        for schema in [*schemas, None]
        for v in connection.execute(views_query(schema and schema)).fetchall()
    ]
