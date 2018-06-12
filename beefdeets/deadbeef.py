"""Interface to DeaDBeeF via it's CLI."""

import re
from subprocess import check_output, call
from os import devnull, listdir
from types import MethodType
from typing import Dict, Callable, List, Union, Optional, Tuple, Set
from copy import copy

from mutagen import File

from .helpers import catch, parse_timestamp


def arg_to_method(arg: str) -> str:
    """Convert a DeaDBeeF argument to a method name."""
    return arg.replace("--", "").replace("-", "_")


def ok(ret_code: int) -> bool:
    """Convert a posix exit code to a boolean."""
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
ACTIONS = {arg_to_method(arg): arg for arg in SINGLE_ARG_COMMANDS}


class Player(object):
    """A DeaDBeeF music player."""

    def __init__(self, path: str) -> None:
        """Initialize a Player.

        Arguments
        ---------
        path : Path to the DeaDBeeF executable.
        """
        self.path = path

        # Add in commands that are just a single CLI argument
        for method_name, arg in ACTIONS.items():
            def _make_method(method_name: str, arg: str) -> Callable[[], bool]:
                def _method(self: Player) -> bool:
                    f"""Perform the {arg} DeaDBeeF CLI command.

                    Returns
                    -------
                    Whether the command executed successfully.
                    """
                    return ok(call(
                        args=[self.path, arg],
                        stderr=open(devnull, "w")
                    ))

                _method.__name__ = method_name
                return MethodType(_method, self)

            setattr(self, method_name, _make_method(method_name, arg))

    def version(self) -> str:
        """Get the DeaDBeeF version."""
        result: str = check_output(
            args=[self.path, "--version"],
            stderr=open(devnull, "w")
        ).decode("utf-8")
        match = re.match(r"DeaDBeeF (\d+\.\d+\.\d+)", result)
        return match.groups()[0] if match else ""

    def now_playing(self, *attrs: str) -> Dict[str, str]:
        """Get information on DeaDBeeF's currently playing track and playlist.

        Arguments
        ---------
        attrs : Attributes to query for.

        Returns
        -------
        Dictionary relating attribute titles to values.
        """
        SENTINEL = "$"
        DIVIDER = "::"

        if len(attrs) == 0:
            return {}

        format_string = SENTINEL + DIVIDER.join([
            f"%{FORMAT_STRINGS[attr]}"
            for attr in attrs
        ])
        result: str = check_output(
            args=[self.path, "--nowplaying", format_string],
            stderr=open(devnull, "w")
        ).decode("utf-8")

        if not result.startswith(SENTINEL):  # An error occured
            return {}

        return dict(zip(attrs, result[len(SENTINEL):].split(DIVIDER)))

    def now_playing_values(self, *attrs: str) -> Tuple[Optional[str], ...]:
        """Get ordered values correspondant to the attributes requested.

        Arguments
        ---------
        attrs : Attributes to query for.

        Returns
        -------
        Corresponding values.
        """
        attrs_dict = self.now_playing(*attrs)
        return tuple([attrs_dict.get(x) for x in attrs])

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
            stderr=open(devnull, "w")
        ))

    def album_cover(self) -> Optional[bytes]:
        """Get the current song's album cover."""
        def from_tags(path: str) -> Optional[bytes]:
            """Get an album cover from a file's meta tags."""
            file = File(path)

            for tag in file.keys():
                if tag.startswith("APIC:"):
                    return file.tags[tag].data

            return None

        @catch(IndexError, AttributeError)
        def from_pics(path: str) -> bytes:
            """Get an album cover from a file's picture metadata."""
            return File(path).pictures[0].data

        def from_dir(directory: str) -> Optional[bytes]:
            """Get an album cover from a folder's cover.jpg."""
            for file in listdir(directory):
                if file.lower() in ["cover.jpg", "cover.jpeg"]:
                    return open(f"{directory}/{file}", "rb").read()

            return None

        path, directory = self.now_playing_values("full_path", "full_dir")

        if path is None or directory is None:
            return None

        return from_tags(path) or from_pics(path) or from_dir(directory)

    def progress(self) -> float:
        """Get the percentage of playback progress for the current song."""
        playback_pos, length = self.now_playing_values("playback_pos", "length")

        if playback_pos is None or length is None:
            return 0.0

        return 100 * (
            parse_timestamp(playback_pos) /
            parse_timestamp(length)
        )
