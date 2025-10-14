from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass, field
from functools import cache, partial, wraps
from typing import Any, Callable


class TrolskgenError(RuntimeError): ...


F = Callable[[Any], ast.AST]
Converter = Callable[[Any, F], ast.AST | None]


def upcast_expr(converter: Converter) -> Converter:
    @wraps(converter)
    def inner(o: Any, f: F) -> ast.AST | None:
        out = converter(o, f)
        if isinstance(out, ast.expr):
            return ast.Module(body=[ast.Expr(value=out)], type_ignores=[])
        return out

    return inner


@cache
def safe_converter_pydantic() -> Converter | None:
    from trolskgen import converters

    try:
        import pydantic  # noqa: F401

        return converters.converter_pydantic
    except ImportError:
        return None


def default_converters() -> list[Converter]:
    from trolskgen import converters

    out: list[Converter] = [
        converters.converter_ast,
        converters.converter_template,
        converters.converter_interface,
        converters.converter_simple,
        converters.converter_types_and_functions,
        converters.converter_typeform,
        converters.converter_common,
    ]
    if (converter_pydantic := safe_converter_pydantic()) is not None:
        out.append(converter_pydantic)
    return out


@dataclass(kw_only=True)
class Config:
    converters: list[Converter] = field(default_factory=default_converters)

    def prepend_converter(self, converter: Converter, *, before: Converter | None = None) -> Config:
        out = Config(converters=[*self.converters])
        i = 0
        if before is not None:
            for i, other in enumerate(out.converters):
                if other is before:
                    break
            else:
                raise TrolskgenError(f"Couldn't find converter: {before}")
        out.converters.insert(i, converter)
        return out


def to_ast(o: Any, *, config: Config | None = None) -> ast.AST:
    if config is None:
        config = Config()
    f = partial(to_ast, config=config)
    for converter in config.converters:
        if (node := converter(o, f)) is not None:
            return node

    raise TrolskgenError(f"No converter matchers: {o!r}")


def sh(cmd: list[str], stdin: str) -> str:
    result = subprocess.run(
        cmd,
        input=stdin,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout


def to_source(
    o: Any,
    *,
    config: Config | None = None,
    ruff_format: bool = False,
    ruff_line_length: int = -1,
) -> str:
    source = ast.unparse(to_ast(o, config=config))
    if ruff_format:
        line_length_args = [] if ruff_line_length == -1 else ["--line-length", str(ruff_line_length)]
        source = sh(["ruff", "format", "-"] + line_length_args, source)
        source = sh(["ruff", "check", "-e", "--fix", "-"], source)
        source = sh(["ruff", "check", "-e", "--select", "I", "--fix", "-"], source)
    return source
