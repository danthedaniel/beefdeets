"""BeeFDeetS web application."""

import io
from functools import wraps
from typing import Callable

from flask import Flask, render_template, jsonify, send_file
from werkzeug.wrappers import Response

from .deadbeef import Player, ACTIONS
from .helpers import nocache, rename


app = Flask(__name__)
app.config.update(dict(
    player=Player("/opt/deadbeef/bin/deadbeef"),
))


def status(response: Response, status_code: int) -> Response:
    """Set the status code for a response."""
    response.status_code = status_code
    return response


def responsify(func: Callable[[], bool]) -> Callable[[], Response]:
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
            app.logger.error(e)
            return status(jsonify({"status": "error", "msg": str(e)}), 500)

    return _wrapper


@app.route("/")
def index():
    """Index route."""
    attrs = app.config["player"].now_playing("artist", "title", "album")

    try:
        title = f"{attrs['album']} - \"{attrs['title']}\" by {attrs['artist']}"
    except KeyError:
        title = "BeeFDeetS"

    return render_template("index.html",
        title=title,
        progress=app.config["player"].progress()
    )


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
@nocache
def album_cover():
    """Get the current song's album cover."""
    cover = app.config["player"].album_cover()
    image = io.BytesIO(cover) if cover else "static/no_cover.jpg"
    return send_file(image, mimetype="image/jpeg")


for method in ACTIONS.keys():
    def _make_route(method: str) -> None:
        @app.route(f"/player/{method}.json", methods=["PATCH"])
        @responsify
        @rename(method)
        def _route() -> bool:
            f"""Perform the player {method} action."""
            return getattr(app.config["player"], method)()

    _make_route(method)
