from typing import NamedTuple, Literal, Union, TypeAlias, Optional, Dict, Tuple

# fmt: off
FileParsingMode: TypeAlias = Union[
    Literal["line"], Literal["chunked"], Literal["raw"]
]

PlaintextEncoding: TypeAlias = Union[
    Literal["base64"], Literal["base64url"], Literal["base32"],
    Literal["base32hex"], Literal["base16"], Literal["plain"]
]
# fmt: on


class Options(NamedTuple):
    mode: FileParsingMode
    plaintext_encoding: Optional[PlaintextEncoding]
    encoding: str = "utf-8"
    recursive: bool = False
    algorithm_options: Optional[Dict] = None


__all__: Tuple[str, ...] = ("Options", "PlaintextEncoding", "FileParsingMode")
