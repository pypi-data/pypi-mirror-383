import pytest
import sqlalchemy.exc
from pytest_mock_resources import create_postgres_fixture
from sqlalchemy import Column, text, types

from sqlalchemy_declarative_extensions import (
    Grants,
    Roles,
    declarative_database,
    register_sqlalchemy_events,
)
from sqlalchemy_declarative_extensions.dialects.postgresql import DefaultGrant
from sqlalchemy_declarative_extensions.grant.compare import compare_grants
from sqlalchemy_declarative_extensions.sqlalchemy import declarative_base

_Base = declarative_base()


@declarative_database
class Base(_Base):  # type: ignore
    __abstract__ = True

    roles = Roles(ignore_unspecified=True).are("foo")
    grants = Grants(default_grants_imply_grants=False).are(
        DefaultGrant.on_tables_in_schema("public").grant("select", "insert", to="foo"),
    )


class Foo(Base):
    __tablename__ = "foo"

    id = Column(types.Integer(), autoincrement=True, primary_key=True)


pg = create_postgres_fixture(scope="function", engine_kwargs={"echo": True})
register_sqlalchemy_events(Base.metadata, schemas=True, roles=True, grants=True)


@pytest.mark.grant
def test_createall_grant(pg):
    with pg.connect() as conn:
        with conn.begin() as trans:
            conn.execute(text("create role foo"))
            conn.execute(text("create table bar (id integer)"))
            trans.commit()

    Base.metadata.create_all(bind=pg)

    # There should be no diffs detected after running `create_all`
    grants = Base.metadata.info["grants"]
    roles = Base.metadata.info["roles"]
    with pg.connect() as conn:
        diff = compare_grants(conn, grants, roles)
    assert len(diff) == 0

    with pg.connect() as conn:
        conn.execute(text("set role foo; SELECT * FROM foo"))
        conn.execute(text("set role foo; INSERT INTO foo VALUES (1)"))

    with pytest.raises(sqlalchemy.exc.ProgrammingError):
        with pg.connect() as conn:
            conn.execute(text("set role foo; SELECT * FROM bar"))

    with pytest.raises(sqlalchemy.exc.ProgrammingError):
        with pg.connect() as conn:
            conn.execute(text("set role foo; INSERT INTO bar VALUES (1)"))
