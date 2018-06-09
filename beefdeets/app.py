"""EFT Version Site."""

import os
import io
from datetime import datetime
from functools import wraps
from typing import Callable, Any

from flask import Flask, render_template, jsonify, g, send_file
from werkzeug.wrappers import Response

from .deadbeef import Player, ACTIONS


app = Flask(__name__)
app.config.update(dict(
    player=Player("/opt/deadbeef/bin/deadbeef"),
))


def status(response: Response, status_code: int) -> Response:
    """Set the status code for a response."""
    response.status_code = status_code
    return response


def statusify(func: Callable[[], bool]) -> Callable[[], Response]:
    """Wrap a function to transform a boolean to a JSON status response."""
    @wraps(func)
    def _wrapper() -> Response:
        try:
            success = func()
            response = jsonify({
                "status": "ok" if success else "error",
                "msg": ""
            })
            return response if success else status(response, 500)
        except Exception as e:
            print(e)
            return status(jsonify({"status": "error", "msg": str(e)}), 500)

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


@app.route("/player/album_cover.jpg")
def album_cover():
    """Get the current song's album cover."""
    cover = app.config["player"].album_cover()
    image = io.BytesIO(cover) if cover else "static/no_cover.jpg"
    return send_file(image, mimetype="image/jpeg")


for method in ACTIONS.keys():
    def _make_route(method):
        def _route() -> bool:
            """Perform the player {} action.""".format(method)
            return getattr(app.config["player"], method)()

        # Set the function name so Flask doesn't have any name collisions
        _route.__name__ = method
        # Manually apply decorators because of the above renaming
        route = statusify(_route)
        app.route("/player/{}.json".format(method), methods=["PATCH"])(route)

    _make_route(method)


if __name__ == "__main__":
    app.run()
