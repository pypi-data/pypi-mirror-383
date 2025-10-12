import os
import tempfile
import pytest
from ddmail_email_remover import create_app

# Set mode to TESTING so we are sure not to run with production configuration running tests.
os.environ["MODE"] = "TESTING"


def pytest_addoption(parser):
    parser.addoption(
        "--config",
        action="store",
        default=None,
        help="Config file to use during test.",
    )
    parser.addoption(
        "--password",
        action="store",
        default=None,
        help="Authentication password to use during test.",
    )


@pytest.fixture(scope="session")
def config_file(request):
    """Fixture to retrieve config file"""
    return request.config.getoption("--config")

@pytest.fixture(scope="session")
def password(request):
    """Fixture to retrieve config file"""
    return request.config.getoption("--password")


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    config_file = session.config.getoption("--config")
    password = session.config.getoption("--password")


@pytest.fixture
def app(config_file):
    """Create and configure a new app instance for each test."""
    # Create the app with common test config
    app = create_app(config_file = config_file)
    app.config.update({
        "TESTING": True,
        "SRM_BIN": "/usr/bin/srm"  # Add SRM_BIN to test configuration
    })

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
