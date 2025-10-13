"""pyreqwest pytest plugin."""

import pytest

from pyreqwest.pytest_plugin.mock import client_mocker as client_mocker  # load the client_mocker fixture

pytest.register_assert_rewrite("pyreqwest.pytest_plugin.internal.assert_eq")


def pytest_configure(config: pytest.Config) -> None:
    """Configure the pytest plugin."""
    config.addinivalue_line(
        "markers",
        "pyreqwest: mark test to use PyReqwest HTTP client mocking",
    )
