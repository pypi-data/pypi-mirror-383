from typing import Tuple

from . import main


def init() -> None:
    if __name__ == "__main__":
        main.main()


init()


__all__: Tuple[str, ...] = ("init",)
