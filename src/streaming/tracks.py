"""
tracks.py
---------
Implement the class hierarchy for all playable content on the platform.

Classes to implement:
  - Track (abstract base class)
    - Song
      - SingleRelease
      - AlbumTrack
    - Podcast
      - InterviewEpisode
      - NarrativeEpisode
    - AudiobookTrack
"""
from __future__ import annotations

from datetime import date


class Track:
    """Base class for all playable content on the platform."""

    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str) -> None:
        self.track_id = track_id
        self.title = title
        self.duration_seconds = duration_seconds
        self.genre = genre

    def duration_minutes(self) -> float:
        return self.duration_seconds / 60

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Track):
            return False
        return self.track_id == other.track_id

    def __hash__(self) -> int:
        return hash(self.track_id)


class Song(Track):
    """A track associated with an artist."""

    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, artist) -> None:
        super().__init__(track_id, title, duration_seconds, genre)
        self.artist = artist


class SingleRelease(Song):
    """A song released as a standalone single with a release date."""

    def __init__(
            self,
            track_id: str,
            title: str,
            duration_seconds: int,
            genre: str,
            artist,
            release_date: date,
    ) -> None:
        super().__init__(track_id, title, duration_seconds, genre, artist)
        self.release_date = release_date


class AlbumTrack(Song):
    """A song that is part of an album, identified by its track number."""

    def __init__(
            self,
            track_id: str,
            title: str,
            duration_seconds: int,
            genre: str,
            artist,
            track_number: int,
    ) -> None:
        super().__init__(track_id, title, duration_seconds, genre, artist)
        self.track_number = track_number
        self.album = None


class Podcast(Track):
    """A spoken-word track hosted by a named host."""

    def __init__(
            self,
            track_id: str,
            title: str,
            duration_seconds: int,
            genre: str,
            host: str,
            description: str = "",
    ) -> None:
        super().__init__(track_id, title, duration_seconds, genre)
        self.host = host
        self.description = description


class InterviewEpisode(Podcast):
    """A podcast episode featuring an interview with a named guest."""

    def __init__(
            self,
            track_id: str,
            title: str,
            duration_seconds: int,
            genre: str,
            host: str,
            guest: str,
            description: str = "",
    ) -> None:
        super().__init__(track_id, title, duration_seconds, genre, host, description)
        self.guest = guest


class NarrativeEpisode(Podcast):
    """A serialised podcast episode identified by season and episode number."""

    def __init__(
            self,
            track_id: str,
            title: str,
            duration_seconds: int,
            genre: str,
            host: str,
            season: int,
            episode_number: int,
            description: str = "",
    ) -> None:
        super().__init__(track_id, title, duration_seconds, genre, host, description)
        self.season = season
        self.episode_number = episode_number


class AudiobookTrack(Track):
    """A track from an audiobook with a named author and narrator."""

    def __init__(
            self,
            track_id: str,
            title: str,
            duration_seconds: int,
            genre: str,
            author: str,
            narrator: str,
    ) -> None:
        super().__init__(track_id, title, duration_seconds, genre)
        self.author = author
        self.narrator = narrator
