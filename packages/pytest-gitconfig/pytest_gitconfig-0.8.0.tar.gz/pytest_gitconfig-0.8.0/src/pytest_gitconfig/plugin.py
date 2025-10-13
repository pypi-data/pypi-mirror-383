from __future__ import annotations

import os
import shutil

from collections.abc import Iterator, Mapping
from configparser import ConfigParser
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NewType

import pytest

DEFAULT_GIT_USER_NAME = "Pytest"
DEFAULT_GIT_USER_EMAIL = "pytest@local.dev"
DEFAULT_GIT_BRANCH = "main"

UnsetType = NewType("UnsetType", object)
UNSET = UnsetType(object())
DELETE = object()


@pytest.fixture(scope="session")
def sessionpatch() -> Iterator[pytest.MonkeyPatch]:
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope="session")
def default_git_user_name() -> str | UnsetType:
    return DEFAULT_GIT_USER_NAME


@pytest.fixture(scope="session")
def default_git_user_email() -> str | UnsetType:
    return DEFAULT_GIT_USER_EMAIL


@pytest.fixture(scope="session")
def default_git_init_default_branch() -> str | UnsetType:
    return DEFAULT_GIT_BRANCH


@pytest.fixture(scope="session")
def git_user_name() -> str | None | UnsetType:
    pass


@pytest.fixture(scope="session")
def git_user_email() -> str | None | UnsetType:
    pass


@pytest.fixture(scope="session")
def git_init_default_branch() -> str | None | UnsetType:
    pass


@dataclass
class GitConfig:
    path: Path

    def __str__(self):
        return str(self.path)

    def set(self, data: Mapping[str, Any]):
        cfg = self._read()
        for section, option, value in self._iter_data(data):
            if not cfg.has_section(section):
                cfg.add_section(section)
            if value is DELETE or value is UNSET:
                cfg.remove_option(section, option)
            else:
                cfg.set(section, option, value)
        self._write(cfg)

    def get(self, key: str, default: Any = UNSET) -> str:
        cfg = self._read()
        section, option = self._parse_key(key)
        try:
            return cfg[section][option]
        except KeyError as e:
            if default is UNSET:
                raise KeyError(f"Key {section}.{option} not found in git config") from e
            return default

    @contextmanager
    def override(self, data: Mapping[str, Any]) -> Iterator[GitConfig]:
        keys = {f"{section}.{option}" for section, option, _ in self._iter_data(data)}
        backup = {key: self.get(key, DELETE) for key in keys}
        self.set(data)
        try:
            yield self
        finally:
            self.set(backup)

    def _iter_data(self, data: Mapping[str, Any]) -> Iterator[tuple[str, str, str]]:
        for key, content in data.items():
            if "." in key:
                # Dotted key
                section, option = key.split(".", 1)
                yield section, option, content
            else:
                # Nested dicts
                for option, value in content.items():
                    yield key, option, value

    def _parse_key(self, key: str) -> list[str]:
        if key.count(".") != 1:
            raise ValueError("git config keys must be in the form of <section>.<option>")
        return key.rsplit(".", 1)

    def _read(self) -> ConfigParser:
        cfg = ConfigParser()
        cfg.read(self.path)
        return cfg

    def _write(self, cfg: ConfigParser):
        with self.path.open("w") as out:
            cfg.write(out)


@pytest.fixture(scope="session", autouse=True)
def default_gitconfig(
    tmp_path_factory: pytest.TempPathFactory,
    sessionpatch: pytest.MonkeyPatch,
    default_git_user_name: str | UnsetType,
    default_git_user_email: str | UnsetType,
    default_git_init_default_branch: str | UnsetType,
) -> GitConfig:
    path = tmp_path_factory.mktemp("git", False) / "config"
    gitconfig = GitConfig(path)

    for var in os.environ:
        if var.startswith("GIT_"):
            sessionpatch.delenv(var, False)
    sessionpatch.setenv("GIT_CONFIG_GLOBAL", str(gitconfig))

    settings: dict[str, Any] = {
        "user.name": default_git_user_name,
        "user.email": default_git_user_email,
        "init.defaultBranch": default_git_init_default_branch,
    }

    gitconfig.set(settings)

    return gitconfig


@pytest.fixture
def gitconfig(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    default_gitconfig: GitConfig,
    git_user_name: str | None,
    git_user_email: str | None,
    git_init_default_branch: str | None,
) -> GitConfig:
    path = tmp_path / "gitconfig"
    shutil.copy(default_gitconfig.path, path)
    gitconfig = GitConfig(path)

    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(gitconfig))

    settings: dict[str, str] = {
        k: v
        for k, v in (
            ("user.name", git_user_name),
            ("user.email", git_user_email),
            ("init.defaultBranch", git_init_default_branch),
        )
        if v is not None
    }

    if settings:
        gitconfig.set(settings)

    return gitconfig
