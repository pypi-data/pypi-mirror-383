import textwrap

import pytest
from typer.testing import CliRunner

from cadwyn import __version__
from cadwyn.__main__ import app


def code(c: str) -> str:
    return "\n".join(line.rstrip() for line in textwrap.dedent(c.strip()).splitlines())


def test__render_module():
    result = CliRunner().invoke(
        app,
        [
            "render",
            "module",
            "tests._resources.render.classes",
            "--app=tests._resources.render.versions:app",
            "--version=2000-01-01",
            "--raw",
        ],
    )
    assert code(result.stdout) == code(
        """
from enum import Enum, auto
from pydantic import BaseModel

class MyEnum(Enum):
    pass

class A(BaseModel):
    pass
"""
    )


def test__render_model():
    result = CliRunner().invoke(
        app,
        [
            "render",
            "model",
            "tests._resources.render.classes:A",
            "--app=tests._resources.render.versions:app",
            "--version=2000-01-01",
            "--raw",
        ],
    )
    assert code(result.stdout) == code(
        """
class A(BaseModel):
    pass
"""
    )


@pytest.mark.parametrize("arg", ["-V", "--version"])
def test__cli_get_version(arg: str) -> None:
    result = CliRunner().invoke(app, [arg])
    assert result.exit_code == 0, result.stdout
    assert result.stdout == f"Cadwyn {__version__}\n"
