import sys
import os.path

from .app import app


def main():
    deadbeef = app.config["player"].path

    if os.path.isfile(deadbeef):
        app.run(host="0.0.0.0", port=8080)
    else:
        print(f"DeaDBeeF executable {deadbeef} does not exist", file=sys.stderr)


if __name__ == "__main__":
    main()
