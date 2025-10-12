import argparse
from typing import Tuple, Type, TYPE_CHECKING

from . import utils, types, algorithm


if TYPE_CHECKING:
    # noinspection PyProtectedMember
    from importlib.metadata import EntryPoints

ALGORITHMS: "EntryPoints" = utils.get_algorithms()


def _is_plain_parsing():
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        exit_on_error=False, add_help=False
    )

    parser.add_argument("--line", action="store_true", dest="plain", default=False)
    parser.add_argument("--chunked", action="store_true", dest="plain", default=False)

    args, _unknown_args = parser.parse_known_args()
    return args.plain


def _add_parsing_strategy_group(parser: argparse.ArgumentParser) -> None:
    group: argparse._ArgumentGroup = parser.add_argument_group(
        "File Parsing Strategy",
        description="Method to extract ciphertext from the provided files.",
    )
    exclusion_group = group.add_mutually_exclusive_group(required=True)
    exclusion_group.add_argument(
        "--line",
        action="store_true",
        help="Interpret non-blank lines in files as encoded ciphertext, such "
        "as when each line contains Base64 that is a separate ciphertext."
        "Opens files in a plain-text mode. Specify encoding with --encoding.",
    )
    exclusion_group.add_argument(
        "--chunked",
        action="store_true",
        help="Interpret all lines in a file as part of one encoded string, such"
        "as when Base64 for a single ciphertext spans multiple lines, which"
        "effectively removes lines to reconstruct the ciphertext. Opens files"
        "in a plain-text mode with encoding specified with --encoding.",
    )
    exclusion_group.add_argument(
        "--raw", action="store_true", help="Interpret all files as binary ciphertext."
    )


def _add_plain_group(parser: argparse.ArgumentParser) -> None:
    group: argparse._ArgumentGroup = parser.add_argument_group(
        "Plaintext Encoding",
        description="Encoding used to decode plaintext input. "
        "Ignored when using raw bytes as ciphertext "
        "and required when using plaintext.",
    )
    exclusion_group = group.add_mutually_exclusive_group(required=_is_plain_parsing())
    exclusion_group.add_argument(
        "--base64",
        action="store_true",
        help="Interpret plain-text content as Base64 " "using the standard alphabet.",
    )
    exclusion_group.add_argument(
        "--base64url",
        action="store_true",
        help="Interpret plain-text content as Base64 "
        "with the filesystem and URL-safe alphabet.",
    )
    exclusion_group.add_argument(
        "--base32",
        action="store_true",
        help="Interpret plain-text content as Base32. "
        "Does not accept the lowercase alphabet and "
        "does not support mapping at this time.",
    )
    exclusion_group.add_argument(
        "--base32hex",
        action="store_true",
        help="Interpret plain-text content ase Base32 using "
        "the extended HEX alphabet. Does not accept "
        "the lowercase alphabet at this time.",
    )
    exclusion_group.add_argument(
        "--base16",
        action="store_true",
        help="Interpret plain-text content ase Base32. "
        "Does not accept the lowercase alphabet.",
    )
    exclusion_group.add_argument(
        "--plain",
        action="store_true",
        help="Interpret plain-text content as simply plain text.",
    )


def _add_algorithm_group(parser: argparse.ArgumentParser) -> None:
    algorithms = utils.get_algorithms()
    parser.add_argument(
        "algorithm", choices=[e.name for e in algorithms], help="The algorithm to use."
    )

    for alg in algorithms:
        handler: Type["algorithm.Algorithm"] = alg.load()
        handler.register_args(alg.name, parser)


def _main_parser():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("--encoding", default="utf-8", help="The encoding to use.")
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        default=False,
        help="Recurse over directories.",
    )

    _add_parsing_strategy_group(parser)
    _add_plain_group(parser)
    _add_algorithm_group(parser)

    parser.add_argument("files", nargs="+", help="Files to parse.")

    return parser


def parse():
    parser = _main_parser()
    args = parser.parse_args()

    # noinspection PyTypeChecker
    mode: types.FileParsingMode = utils.get_truthy_attribute(
        args, ("raw", "line", "chunked"), fallback="raw"
    )

    plaintext_encoding = utils.get_truthy_attribute(
        args, ("base64", "base64url", "base32", "base32hex", "base16", "plain")
    )

    algorithm_handler: Type["algorithm.Algorithm"] = ALGORITHMS[args.algorithm].load()
    return (
        algorithm_handler,
        args.files,
        types.Options(
            mode=mode,
            plaintext_encoding=plaintext_encoding,
            encoding=args.encoding,
            recursive=args.recursive,
            algorithm_options=algorithm_handler.extract_args(args.algorithm, args),
        ),
    )


__all__: Tuple[str, ...] = ("parse",)
