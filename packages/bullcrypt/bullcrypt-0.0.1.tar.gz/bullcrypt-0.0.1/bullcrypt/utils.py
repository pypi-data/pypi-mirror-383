import base64
import pathlib
from importlib.metadata import entry_points
from typing import Any, Sequence, Tuple, Dict, Callable, TypeVar, Union, Optional

from . import types


def get_algorithms():
    return entry_points(group="bullcrypt.algorithm")


T = TypeVar("T")
U = TypeVar("U")


def get_truthy_attribute(
    obj: Any, options: Sequence[T], fallback: U = None
) -> Union[T, U]:
    for option in options:
        if getattr(obj, option, False):
            return option

    return fallback


DECODERS: Dict[str, Callable[[str], bytes]] = {
    "base64": base64.b64decode,
    "base64url": base64.urlsafe_b64decode,
    "base32": base64.b32decode,
    "base32hex": base64.b32hexdecode,
    "base16": base64.b16decode,
}


def decode_content(
    content: str,
    plaintext_encoding: Optional[types.PlaintextEncoding],
    encoding: str,
) -> bytes:
    if plaintext_encoding is None or plaintext_encoding == "plain":
        return content.encode(encoding)

    return DECODERS[plaintext_encoding](content)


def extract_content(
    file_path: pathlib.Path,
    mode: types.FileParsingMode,
    plaintext_encoding: Optional[types.PlaintextEncoding],
    encoding: str,
):
    if mode == "raw":
        with open(file_path, "rb", encoding=encoding) as file:
            yield file.read()
    elif mode == "chunked":
        with open(file_path, "r", encoding=encoding) as file:
            yield decode_content(
                "".join(file.read().splitlines()),
                plaintext_encoding,
                encoding,
            )
    elif mode == "line":
        with open(file_path, "r", encoding=encoding) as file:
            for line in file:
                line = line.strip()
                if line:
                    yield decode_content(line, plaintext_encoding, encoding)


__all__: Tuple[str, ...] = ("get_algorithms", "get_truthy_attribute")
