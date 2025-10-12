import argparse
from typing import Optional, Dict, Tuple

from cryptography.fernet import Fernet as _Fernet

from .. import types
from ..algorithm import Algorithm


class Fernet(Algorithm):
    @classmethod
    def decrypt(cls, payload: bytes, options: types.Options):
        key = _Fernet(options.algorithm_options["key"].encode(options.encoding))
        return key.decrypt(payload)

    # noinspection PyUnusedLocal
    @classmethod
    def register_args(cls, algorithm_name: str, parser):
        group = parser.add_argument_group(f"Fernet ({algorithm_name})")
        group.add_argument(
            f"--{algorithm_name}.key",
            dest=f"{algorithm_name}.key",
            help="A 32-byte key encoded as Base64URL",
        )

    # noinspection PyUnusedLocal
    @classmethod
    def extract_args(
        cls, algorithm_name: str, args: argparse.Namespace
    ) -> Optional[Dict]:
        key: Optional[str] = getattr(args, f"{algorithm_name}.key")
        if not key:
            raise ValueError(
                "A Fernet key is required and must be 32 url-safe base64-encoded bytes."
            )

        return {
            "key": key,
        }


__all__: Tuple[str, ...] = ("Fernet",)
