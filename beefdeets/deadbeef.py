from subprocess import check_output, call
from os import devnull
from functools import wraps
from typing import Dict, Callable, List


def arg_to_method(arg: str) -> str:
    """Convert a DEADBEEF argument to a method name."""
    return arg.replace("--", "").replace("-", "_")


def ok(ret_code: int) -> bool:
    """Convert a UNIX return code to a boolean."""
    return ret_code == 0


FORMAT_STRINGS = {
    "artist": "a",
    "title": "t",
    "album": "b",
    "band": "B",
    "track_num": "n",
    "numtracks": "N",
    "length": "l",
    "playback_pos": "e",
    "year": "y",
    "genre": "g",
    "comment": "c",
    "composer": "C",
    "copyright": "r",
    "tags": "T",
    "path": "f",
    "full_path": "F",
    "dir": "d",
    "full_dir": "D",
    "playlist_num": "X",
    "playlist_length": "L",
    "channels": "Z",
    "version": "V"
}

SINGLE_ARG_COMMANDS = [
    "--toggle-pause",
    "--pause",
    "--next",
    "--prev",
    "--random",
    "--play",
    "--stop",
    "--play-pause"
]
SIMPLE_METHODS = {arg_to_method(arg): arg for arg in SINGLE_ARG_COMMANDS}


class Player(object):
    """A DEADBEEF music player."""

    def __init__(self, path: str) -> None:
        """Initialize a Player.

        Arguments
        ---------
        path : Path to the DEADBEEF executable.
        """
        self.path = path

        # Add in commands that are just a single CLI argument
        for method_name, arg in SIMPLE_METHODS.items():
            def _method(self: Player) -> bool:
                """Perform the {} DEADBEEF CLI command.

                Returns
                -------
                Whether the command executed successfully.
                """.format(arg)
                return ok(call(
                    args=[self.path, arg],
                    stderr=open("/dev/null", "w")
                ))
            _method.__name__ = method_name
            setattr(self, method_name, _method)

    def version(self) -> str:
        """Get the DEADBEEF version."""
        return self.now_playing("version")["version"]

    def now_playing(self, *attrs: str) -> Dict[str, str]:
        """Get information on DEADBEEF's currently playing track and playlist.

        Arguments
        ---------
        path : Path to the deadbeef executable.
        attrs : Attributes to query for.

        Returns
        -------
        Dictionary relating attribute titles to values.
        """
        if len(attrs) == 0:
            return {}

        format_string = "::".join([
            "%{}".format(FORMAT_STRINGS[attr])
            for attr in attrs
        ])
        result: str = check_output(
            args=[self.path, "--nowplaying", format_string],
            stderr=open(devnull, "w")
        ).decode("utf-8")
        return dict(zip(attrs, result.split("::")))

    def enqueue(self, songs: List[str]) -> bool:
        """Add a list of songs to the play queue.

        Arguments
        ---------
        songs : Paths to songs.

        Returns
        -------
        Whether the command executed successfully.
        """
        return ok(call(
            args=[self.path, "--queue", *songs],
            stderr=open("/dev/null", "w")
        ))
