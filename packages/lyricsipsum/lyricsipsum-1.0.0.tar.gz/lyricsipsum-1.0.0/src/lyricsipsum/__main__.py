#!/usr/bin/env python -B
# vi: set syntax=python ts=4 sw=4 sts=4 et ff=unix ai si :
#
# (c) Steven Scholnick <scholnicks@gmail.com>
# The lyricsipsum source code is published under a MIT license.

"""
lyricsipsum: Generates Lorem Ipsum text using song lyrics lyrics

Usage:
    lyricsipsum [options]

Options:
    -h, --help          Show this help screen
    -n, --number=<num>  Number of songs to download [default: 50]
    -s, --save=<artist> Save lyrics to file for <artist>
    -t, --title         Print the song title along with the lyrics
    -v, --verbose       Enable verbose mode
    --version           Prints the version
"""

import json
import os
import random
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from docopt import docopt
from lyricsgenius import Genius

arguments: dict = {}


@dataclass
class Song:
    title: str
    lyrics: str


def main() -> None:
    """Main Method"""
    global arguments
    arguments = docopt(__doc__, version="lyricsipsum 1.0.0")

    if arguments["--save"]:
        saveLyricsToFile()
    else:
        song: Song = random.choice(readLyricsFromFile())
        if arguments["--title"]:
            print(f"{song.title}\n\n{song.lyrics}\n")
        else:
            print(f"\n{song.lyrics}\n")
    sys.exit(0)


def readLyricsFromFile() -> list[Song]:
    """Reads lyrics from a file and returns a list of Song objects"""
    try:
        with open(jsonPath(), "r") as f:
            return [Song(**song) for song in json.load(f)]
    except FileNotFoundError:
        print(f"No lyrics file found at {jsonPath()}. Please run with --save to create one.")
        sys.exit(1)


def saveLyricsToFile() -> None:
    """Fetches lyrics from Genius and saves them to a file"""

    genius: Genius = Genius(os.environ.get("GENIUS_ACCESS_TOKEN", ""))
    genius.verbose = arguments["--verbose"]
    genius.skip_non_songs = True
    genius.excluded_terms = ["(Remix)", "(Live)"]
    genius.remove_section_headers = True
    genius.timeout = 15

    songs: list[Song] = readLyricsFromFile() if Path(jsonPath()).exists() else []
    artist = genius.search_artist(arguments["--save"], max_songs=int(arguments["--number"]), sort="popularity")
    for song in artist.songs:
        if song.lyrics:
            songs.append(Song(title=song.title, lyrics=re.sub(r"\n+", "\n", song.lyrics).strip()))

    with open(Path.home() / ".lyricsipsum.json", "w") as f:
        json.dump([asdict(s) for s in songs], f, indent=4)

    print(f"Saved {len(songs)} songs to {jsonPath()}")


def jsonPath() -> str:
    """Returns the path to the JSON file containing lyrics"""
    return str(Path.home() / ".lyricsipsum.json")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
