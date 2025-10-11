"""Unit tests for DatabaseConfiguration model."""

from pathlib import Path

import pytest

from pydantic import ValidationError

from models.config import (
    PostgreSQLDatabaseConfiguration,
    SQLiteDatabaseConfiguration,
    DatabaseConfiguration,
)


def test_database_configuration(subtests) -> None:
    """Test the database configuration handling."""
    with subtests.test(msg="PostgreSQL"):
        d1 = PostgreSQLDatabaseConfiguration(
            db="db",
            user="user",
            password="password",
            port=1234,
            ca_cert_path=Path("tests/configuration/server.crt"),
        )
        d = DatabaseConfiguration(postgres=d1)
        assert d is not None
        assert d.sqlite is None
        assert d.postgres is not None
        assert d.db_type == "postgres"
        assert d.config is d1

    with subtests.test(msg="SQLite"):
        d1 = SQLiteDatabaseConfiguration(
            db_path="/tmp/foo/bar/baz",
        )
        d = DatabaseConfiguration(sqlite=d1)
        assert d is not None
        assert d.sqlite is not None
        assert d.postgres is None
        assert d.db_type == "sqlite"
        assert d.config is d1


def test_no_databases_configuration() -> None:
    """Test if no databases configuration is checked."""
    d = DatabaseConfiguration()
    assert d is not None

    # default should be SQLite when nothing is provided
    assert d.db_type == "sqlite"

    # simulate no DB configuration
    d.sqlite = None
    d.postgres = None

    with pytest.raises(ValueError, match="No database configuration found"):
        # access property to call its getter
        _ = d.db_type

    with pytest.raises(ValueError, match="No database configuration found"):
        # access property to call its getter
        _ = d.config


def test_two_databases_configuration() -> None:
    """Test if two databases configuration is checked."""
    d1 = PostgreSQLDatabaseConfiguration(db="db", user="user", password="password")
    d2 = SQLiteDatabaseConfiguration(db_path="foo_bar_baz")
    with pytest.raises(
        ValidationError, match="Only one database configuration can be provided"
    ):
        DatabaseConfiguration(postgres=d1, sqlite=d2)
