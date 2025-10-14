from pathlib import Path
import re
from typing import Any, Callable, TypeAlias, TypeVar, overload

T = TypeVar("T")
StringConverter: TypeAlias = Callable[[str], T]
Separator: TypeAlias = str | re.Pattern[str]

@overload
def parse_string(
    string: str, separators: tuple[()], converter: StringConverter[T] | None = None
) -> T: ...
@overload
def parse_string(
    string: str,
    separators: tuple[Separator],
    converter: StringConverter[T] | None = None,
) -> list[T]: ...
@overload
def parse_string(
    string: str,
    separators: tuple[Separator, Separator],
    converter: StringConverter[T] | None = None,
) -> list[list[T]]: ...
@overload
def parse_string(
    string: str,
    separators: tuple[Separator, Separator, Separator],
    converter: StringConverter[T] | None = None,
) -> list[list[list[T]]]: ...
@overload
def parse_string(
    string: str,
    separators: tuple[Separator, Separator, Separator, Separator],
    converter: StringConverter[T] | None = None,
) -> list[list[list[list[T]]]]: ...
@overload
def parse_string(
    string: str,
    separators: tuple[Separator, Separator, Separator, Separator, Separator],
    converter: StringConverter[T] | None = None,
) -> list[list[list[list[list[T]]]]]: ...
@overload
def parse_string(
    string: str,
    separators: tuple[Separator, ...],
    converter: StringConverter[T] | None = None,
) -> list[Any]: ...
@overload
def parse_file_content(
    filepath: str | Path,
    separators: tuple[()],
    converter: StringConverter[T] | None = None,
) -> T: ...
@overload
def parse_file_content(
    filepath: str | Path,
    separators: tuple[Separator],
    converter: StringConverter[T] | None = None,
) -> list[T]: ...
@overload
def parse_file_content(
    filepath: str | Path,
    separators: tuple[Separator, Separator],
    converter: StringConverter[T] | None = None,
) -> list[list[T]]: ...
@overload
def parse_file_content(
    filepath: str | Path,
    separators: tuple[Separator, Separator, Separator],
    converter: StringConverter[T] | None = None,
) -> list[list[list[T]]]: ...
@overload
def parse_file_content(
    filepath: str | Path,
    separators: tuple[Separator, Separator, Separator, Separator],
    converter: StringConverter[T] | None = None,
) -> list[list[list[list[T]]]]: ...
@overload
def parse_file_content(
    filepath: str | Path,
    separators: tuple[Separator, Separator, Separator, Separator, Separator],
    converter: StringConverter[T] | None = None,
) -> list[list[list[list[list[T]]]]]: ...
@overload
def parse_file_content(
    filepath: str | Path,
    separators: tuple[Separator, ...],
    converter: StringConverter[T] | None = None,
) -> list[Any]: ...
def b64encode(text: str, times_to_encode: int = 1) -> str: ...
def b64decode(text: str, times_to_decode: int = 1) -> str: ...
