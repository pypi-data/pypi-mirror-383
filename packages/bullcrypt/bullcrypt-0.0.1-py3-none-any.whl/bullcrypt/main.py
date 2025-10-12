import pathlib
from typing import TYPE_CHECKING, Type, Tuple

from . import cli, types


if TYPE_CHECKING:
    from . import algorithm


def _decrypt_file(
    handler: Type["algorithm.Algorithm"],
    file_path: pathlib.Path,
    options: types.Options,
):
    for payload in handler.extract_content(file_path, options):
        result = handler.decrypt(payload, options).decode(options.encoding)
        print(f"{file_path} -> {result}")


def _process_file(
    handler: Type["algorithm.Algorithm"], file_path: str, options: types.Options
) -> None:
    normalized_path = pathlib.Path(file_path)
    if normalized_path.is_file():
        _decrypt_file(handler, normalized_path, options)
    elif options.recursive and normalized_path.is_dir():
        for entry_path in normalized_path.rglob("*"):
            # pylint: disable=try-except-raise,broad-exception-caught
            try:
                _decrypt_file(handler, entry_path, options)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"Failed to process file: {entry_path} ({e})")


def main():
    handler, files, options = cli.parse()

    for file in files:
        # pylint: disable=broad-exception-caught,try-except-raise
        try:
            _process_file(handler, file, options)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"Failed to process file: {file} ({e})")


__all__: Tuple[str, ...] = ("main",)
