from __future__ import annotations

import os

import pytest

from pytest_gitconfig import GitConfig

USER_NAME = "Overridden user Name"
USER_EMAIL = "hello@nowhere.com"
DEFAULT_BRANCH = "any_branch"

pytestmark = pytest.mark.mypy_testing


@pytest.fixture
def git_user_name() -> str:
    return USER_NAME


@pytest.fixture
def git_user_email() -> str:
    return USER_EMAIL


@pytest.fixture
def git_init_default_branch() -> str:
    return DEFAULT_BRANCH


def test_gitconfig_fixture_override_defaults(
    default_gitconfig: GitConfig,
    default_git_user_name: str,
    default_git_user_email: str,
    default_git_init_default_branch: str,
):
    assert default_gitconfig.get("user.name") == default_git_user_name
    assert default_gitconfig.get("user.email") == default_git_user_email
    assert default_gitconfig.get("init.defaultBranch") == default_git_init_default_branch
    assert "GIT_WHATEVER" not in os.environ


def test_gitconfig_fixture_override(gitconfig: GitConfig):
    assert gitconfig.get("user.name") == USER_NAME
    assert gitconfig.get("user.email") == USER_EMAIL
    assert gitconfig.get("init.defaultBranch") == DEFAULT_BRANCH
    assert "GIT_WHATEVER" not in os.environ
