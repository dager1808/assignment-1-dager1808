"""
artists.py
----------
Implement the Artist class representing musicians and content creators.

Classes to implement:
  - Artist
"""


class Artist:
    """A musician or content creator with a primary genre."""

    def __init__(self, artist_id: str, name: str, genre: str) -> None:
        self.artist_id = artist_id
        self.name = name
        self.genre = genre
        self.tracks: list = []

    def add_track(self, track) -> None:
        self.tracks.append(track)

    def track_count(self) -> int:
        return len(self.tracks)
