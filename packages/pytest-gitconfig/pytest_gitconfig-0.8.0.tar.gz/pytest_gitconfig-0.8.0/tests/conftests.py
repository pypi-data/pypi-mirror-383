from __future__ import annotations

import pytest

pytest_plugins = "pytester"


@pytest.fixture(scope="session", autouse=True)
def git_env_var(sessionpatch: pytest.MonkeyPatch):
    sessionpatch.setenv("GIT_WHATEVER", "whatever")


@pytest.fixture(scope="session")
def default_git_user_name() -> str:
    return "default user"


@pytest.fixture(scope="session")
def default_git_user_email() -> str:
    return "default@py.test"


@pytest.fixture(scope="session")
def default_git_init_default_branch() -> str:
    return "master"
