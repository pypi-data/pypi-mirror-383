"""Unit tests for app.database module."""

# pylint: disable=protected-access

from pathlib import Path
import tempfile
import pytest
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from app import database
from models.config import SQLiteDatabaseConfiguration, PostgreSQLDatabaseConfiguration


@pytest.fixture(name="reset_database_state")
def reset_database_state_fixture():
    """Reset global database state before and after tests."""
    original_engine = database.engine
    original_session_local = database.SessionLocal

    # Reset state before test
    database.engine = None
    database.SessionLocal = None

    yield

    # Restore original state after test
    database.engine = original_engine
    database.SessionLocal = original_session_local


@pytest.fixture(name="base_postgres_config")
def base_postgres_config_fixture():
    """Provide base PostgreSQL configuration for tests."""
    return PostgreSQLDatabaseConfiguration(
        host="localhost",
        port=5432,
        db="testdb",
        user="testuser",
        password="testpass",
        namespace="public",
    )


@pytest.mark.usefixtures("reset_database_state")
class TestGetEngine:
    """Test cases for get_engine function."""

    def test_get_engine_when_initialized(self, mocker):
        """Test get_engine returns engine when initialized."""
        mock_engine = mocker.MagicMock(spec=Engine)
        database.engine = mock_engine

        result = database.get_engine()

        assert result is mock_engine

    def test_get_engine_when_not_initialized(self):
        """Test get_engine raises RuntimeError when not initialized."""
        database.engine = None

        with pytest.raises(RuntimeError, match="Database engine not initialized"):
            database.get_engine()


@pytest.mark.usefixtures("reset_database_state")
class TestGetSession:
    """Test cases for get_session function."""

    def test_get_session_when_initialized(self, mocker):
        """Test get_session returns session when initialized."""
        mock_session_local = mocker.MagicMock()
        mock_session = mocker.MagicMock(spec=Session)
        mock_session_local.return_value = mock_session
        database.SessionLocal = mock_session_local

        result = database.get_session()

        assert result is mock_session
        mock_session_local.assert_called_once()

    def test_get_session_when_not_initialized(self):
        """Test get_session raises RuntimeError when not initialized."""
        database.SessionLocal = None

        with pytest.raises(RuntimeError, match="Database session not initialized"):
            database.get_session()


class TestCreateTables:
    """Test cases for create_tables function."""

    def test_create_tables_success(self, mocker):
        """Test create_tables calls Base.metadata.create_all with engine."""
        mock_base = mocker.patch("app.database.Base")
        mock_get_engine = mocker.patch("app.database.get_engine")
        mock_engine = mocker.MagicMock(spec=Engine)
        mock_get_engine.return_value = mock_engine

        database.create_tables()

        mock_get_engine.assert_called_once()
        mock_base.metadata.create_all.assert_called_once_with(mock_engine)

    def test_create_tables_when_engine_not_initialized(self, mocker):
        """Test create_tables raises error when engine not initialized."""
        mock_get_engine = mocker.patch("app.database.get_engine")
        mock_get_engine.side_effect = RuntimeError("Database engine not initialized")

        with pytest.raises(RuntimeError, match="Database engine not initialized"):
            database.create_tables()


class TestCreateSqliteEngine:
    """Test cases for _create_sqlite_engine function."""

    def test_create_sqlite_engine_success(self):
        """Test _create_sqlite_engine creates engine successfully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            config = SQLiteDatabaseConfiguration(db_path=str(db_path))

            engine = database._create_sqlite_engine(config)

            assert isinstance(engine, Engine)
            assert f"sqlite:///{db_path}" in str(engine.url)

    def test_create_sqlite_engine_directory_not_exists(self):
        """Test _create_sqlite_engine raises error when directory doesn't exist."""
        config = SQLiteDatabaseConfiguration(db_path="/nonexistent/path/test.db")

        with pytest.raises(
            FileNotFoundError, match="SQLite database directory does not exist"
        ):
            database._create_sqlite_engine(config)

    def test_create_sqlite_engine_creation_failure(self, mocker):
        """Test _create_sqlite_engine handles engine creation failure."""
        mock_create_engine = mocker.patch("app.database.create_engine")
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            config = SQLiteDatabaseConfiguration(db_path=str(db_path))
            mock_create_engine.side_effect = Exception("Engine creation failed")

            with pytest.raises(RuntimeError, match="SQLite engine creation failed"):
                database._create_sqlite_engine(config)


class TestCreatePostgresEngine:
    """Test cases for _create_postgres_engine function."""

    def test_create_postgres_engine_success_default_schema(
        self, mocker, base_postgres_config
    ):
        """Test _create_postgres_engine creates engine successfully with default schema."""
        mock_create_engine = mocker.patch("app.database.create_engine")
        mock_engine = mocker.MagicMock(spec=Engine)
        mock_create_engine.return_value = mock_engine

        result = database._create_postgres_engine(base_postgres_config)

        assert result is mock_engine
        # Verify URL construction
        expected_url = (
            "postgresql://testuser:testpass@localhost:5432/testdb?"
            "sslmode=prefer&gssencmode=prefer"
        )
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args
        assert expected_url == call_args[0][0]

    def test_create_postgres_engine_success_custom_schema(
        self, mocker, base_postgres_config
    ):
        """Test _create_postgres_engine creates engine successfully with custom schema."""
        mock_create_engine = mocker.patch("app.database.create_engine")
        mock_engine = mocker.MagicMock(spec=Engine)
        mock_connection = mocker.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        config = base_postgres_config.model_copy(update={"namespace": "custom_schema"})

        result = database._create_postgres_engine(config)

        assert result is mock_engine
        # Verify connect_args for custom schema
        call_args = mock_create_engine.call_args
        assert call_args[1]["connect_args"]["options"] == "-csearch_path=custom_schema"
        # Verify schema creation
        mock_connection.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_create_postgres_engine_with_ca_cert(self, mocker, base_postgres_config):
        """Test _create_postgres_engine with CA certificate path."""
        mock_create_engine = mocker.patch("app.database.create_engine")
        mock_engine = mocker.MagicMock(spec=Engine)
        mock_create_engine.return_value = mock_engine

        with tempfile.NamedTemporaryFile() as cert_file:
            config = base_postgres_config.model_copy(
                update={"ca_cert_path": cert_file.name}
            )

            result = database._create_postgres_engine(config)

            assert result is mock_engine
            call_args = mock_create_engine.call_args
            assert call_args[1]["connect_args"]["sslrootcert"] == cert_file.name

    def test_create_postgres_engine_creation_failure(
        self, mocker, base_postgres_config
    ):
        """Test _create_postgres_engine handles engine creation failure."""
        mock_create_engine = mocker.patch("app.database.create_engine")
        mock_create_engine.side_effect = Exception("Connection failed")

        with pytest.raises(RuntimeError, match="PostgreSQL engine creation failed"):
            database._create_postgres_engine(base_postgres_config)

    def test_create_postgres_engine_schema_creation_failure(
        self, mocker, base_postgres_config
    ):
        """Test _create_postgres_engine handles schema creation failure."""
        mock_create_engine = mocker.patch("app.database.create_engine")
        mock_engine = mocker.MagicMock(spec=Engine)
        mock_connection = mocker.MagicMock()
        mock_connection.execute.side_effect = Exception("Schema creation failed")
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        config = base_postgres_config.model_copy(update={"namespace": "custom_schema"})

        with pytest.raises(RuntimeError, match="Schema creation failed"):
            database._create_postgres_engine(config)


@pytest.mark.usefixtures("reset_database_state")
class TestInitializeDatabase:
    """Test cases for initialize_database function."""

    def _setup_common_mocks(
        self, *, mocker, mock_sessionmaker, mock_logger, enable_debug=False
    ):
        """Setup common mocks for initialize_database tests."""
        mock_engine = mocker.MagicMock(spec=Engine)
        mock_session_local = mocker.MagicMock()
        mock_sessionmaker.return_value = mock_session_local
        mock_logger.isEnabledFor.return_value = enable_debug
        return mock_engine, mock_session_local

    def _verify_common_assertions(
        self, *, mock_sessionmaker, mock_engine, mock_session_local
    ):
        """Verify common assertions for initialize_database tests."""
        mock_sessionmaker.assert_called_once_with(
            autocommit=False, autoflush=False, bind=mock_engine
        )
        assert database.engine is mock_engine
        assert database.SessionLocal is mock_session_local

    def test_initialize_database_sqlite(
        self,
        mocker,
    ):
        """Test initialize_database with SQLite configuration."""
        # Setup mocks
        mock_configuration = mocker.patch("app.database.configuration")
        mock_create_sqlite_engine = mocker.patch("app.database._create_sqlite_engine")
        mock_sessionmaker = mocker.patch("app.database.sessionmaker")
        mock_logger = mocker.patch("app.database.logger")

        mock_engine, mock_session_local = self._setup_common_mocks(
            mocker=mocker, mock_sessionmaker=mock_sessionmaker, mock_logger=mock_logger
        )
        mock_create_sqlite_engine.return_value = mock_engine

        mock_db_config = mocker.MagicMock()
        mock_db_config.db_type = "sqlite"
        mock_db_config.config = SQLiteDatabaseConfiguration(db_path="/tmp/test.db")
        mock_configuration.database_configuration = mock_db_config

        # Call function
        database.initialize_database()

        # Verify calls
        mock_create_sqlite_engine.assert_called_once_with(
            mock_db_config.config, echo=False, pool_pre_ping=True
        )
        self._verify_common_assertions(
            mock_sessionmaker=mock_sessionmaker,
            mock_engine=mock_engine,
            mock_session_local=mock_session_local,
        )

    def test_initialize_database_postgres(
        self,
        mocker,
        base_postgres_config,
    ):
        """Test initialize_database with PostgreSQL configuration."""
        # Setup mocks
        mock_configuration = mocker.patch("app.database.configuration")
        mock_create_postgres_engine = mocker.patch(
            "app.database._create_postgres_engine"
        )
        mock_sessionmaker = mocker.patch("app.database.sessionmaker")
        mock_logger = mocker.patch("app.database.logger")

        mock_engine, mock_session_local = self._setup_common_mocks(
            mocker=mocker,
            mock_sessionmaker=mock_sessionmaker,
            mock_logger=mock_logger,
            enable_debug=True,
        )
        mock_create_postgres_engine.return_value = mock_engine

        mock_db_config = mocker.MagicMock()
        mock_db_config.db_type = "postgres"
        mock_db_config.config = base_postgres_config
        mock_configuration.database_configuration = mock_db_config

        # Call function
        database.initialize_database()

        # Verify calls
        mock_create_postgres_engine.assert_called_once_with(
            mock_db_config.config,
            echo=True,  # Should be True when logger debug is enabled
            pool_pre_ping=True,
        )
        self._verify_common_assertions(
            mock_sessionmaker=mock_sessionmaker,
            mock_engine=mock_engine,
            mock_session_local=mock_session_local,
        )
