#!/usr/bin/env python3

import sys
import argparse
import os.path

from .app import app


def start_app(host: str, port: int) -> None:
    deadbeef = app.config["player"].path

    if os.path.isfile(deadbeef):
        app.run(host=host, port=port)
    else:
        print(f"DeaDBeeF executable {deadbeef} does not exist", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(prog="beefdeets",
        description="Web UI to control DeaDBeeF.")
    parser.add_argument("host", nargs='?', action="store", type=str,
        default="0.0.0.0", help="Address to bind to.")
    parser.add_argument("port", nargs='?', action="store", type=int,
        default=8080, help="Port to bind to.")
    args = parser.parse_args()
    start_app(args.host, args.port)


if __name__ == "__main__":
    main()
