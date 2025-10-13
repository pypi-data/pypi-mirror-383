from __future__ import annotations

import os

import pytest

from pytest_gitconfig import (
    DEFAULT_GIT_BRANCH,
    DEFAULT_GIT_USER_EMAIL,
    DEFAULT_GIT_USER_NAME,
    GitConfig,
)
from pytest_gitconfig.plugin import UNSET, UnsetType

pytestmark = pytest.mark.mypy_testing


@pytest.fixture
def git_user_name() -> str | UnsetType:
    return UNSET


@pytest.fixture
def git_user_email() -> str | UnsetType:
    return UNSET


@pytest.fixture
def git_init_default_branch() -> str | UnsetType:
    return UNSET


def test_gitconfig_fixture_override_defaults(default_gitconfig: GitConfig):
    assert default_gitconfig.get("user.name") == DEFAULT_GIT_USER_NAME
    assert default_gitconfig.get("user.email") == DEFAULT_GIT_USER_EMAIL
    assert default_gitconfig.get("init.defaultBranch") == DEFAULT_GIT_BRANCH
    assert "GIT_WHATEVER" not in os.environ


def test_gitconfig_fixture_override(gitconfig: GitConfig):
    with pytest.raises(KeyError):
        gitconfig.get("user.name")
    with pytest.raises(KeyError):
        gitconfig.get("user.email")
    with pytest.raises(KeyError):
        gitconfig.get("init.defaultBranch")
    assert "GIT_WHATEVER" not in os.environ
