from __future__ import annotations

import importlib.metadata

import lab_orchestration as m


def test_version() -> None:
    assert importlib.metadata.version("lab_orchestration") == m.__version__
