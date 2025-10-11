"""Tests for mixtrain CLI commands."""

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner
from mixtrain.cli import app, __version__


runner = CliRunner()

env = {
    "MIXTRAIN_PLATFORM_URL": "http://localhost:8000/api/v1",
    "MIXTRAIN_API_KEY": "mix-c213cf62f7ad75e50e4abc03ccd5176356851c32fd091f482934716581fa03ce"
}

def test_app_version():
    result = runner.invoke(app, ["--version"], env=env)
    assert result.exit_code == 0
    assert "mixtrain" in result.stdout
    assert __version__ in result.stdout


def test_app_secret_list():
    result = runner.invoke(app, ["secret", "list"], env=env)
    assert result.exit_code == 0
    assert "No secrets found" in result.stdout
    assert "mixtrain secret set" in result.stdout