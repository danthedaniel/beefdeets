"""EFT Version Site."""

from flask import Flask, render_template, jsonify, g
import os
from datetime import datetime
from functools import wraps
from typing import Callable, Any
from .deadbeef import Player, SIMPLE_METHODS


app = Flask(__name__)
app.config.update(dict(
    player=Player("/opt/deadbeef/bin/deadbeef"),
))


def statusify(func: Callable[[], bool]) -> Callable[[], Any]:
    @wraps(func)
    def _wrapper():
        try:
            command_ret = func()
            response = jsonify({
                "status": "ok" if command_ret == 0 else "error",
                "msg": "Success"
            })

            if command_ret != 0:
                response.status_code = 500

            return response
        except Exception as e:
            response = jsonify({"status": "error", "msg": str(e)})
            response.status_code = 500
            return response

    return _wrapper


@app.route("/")
def index():
    """Index route."""
    return render_template("index.html")


@app.route("/player/now_playing.json")
def now_playing():
    """Get attributes for the current song/playlist."""
    return jsonify(
        app.config["player"].now_playing(
            "artist",
            "title",
            "album",
            "playback_pos",
            "length"
        )
    )


@app.route("/player/version.json")
def version():
    """Get the player version."""
    return jsonify({"version": app.config["player"].version()})


for method in SIMPLE_METHODS.keys():
    def _route() -> bool:
        """Perform the player {} action.""".format(method)
        return getattr(app.config["player"], method)()

    # Set the function name so Flask doesn't have any name collisions
    _route.__name__ = method
    # Manually apply decorators because of the above renaming
    route = statusify(_route)
    route = app.route("/player/{}.json".format(method), methods=["PATCH"])(route)

    locals()[method] = route


if __name__ == "__main__":
    app.run()
