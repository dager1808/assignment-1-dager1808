"""
platform.py
-----------
Implement the central StreamingPlatform class that orchestrates all domain entities
and provides query methods for analytics.

Classes to implement:
  - StreamingPlatform
"""
from __future__ import annotations

from streaming.tracks import Song
from streaming.users import PremiumUser, FamilyMember
from streaming.playlists import CollaborativePlaylist
from datetime import datetime, timedelta


class StreamingPlatform:
    def __init__(self, name: str) -> None:
        self.name = name
        self._tracks = []
        self._users = []
        self._artists = []
        self._albums = []
        self._playlists = []
        self._sessions = []

    # ---------- Registration methods ----------

    def add_track(self, track) -> None:
        self._tracks.append(track)

    def add_user(self, user) -> None:
        self._users.append(user)

    def add_artist(self, artist) -> None:
        self._artists.append(artist)

    def add_album(self, album) -> None:
        self._albums.append(album)

    def add_playlist(self, playlist) -> None:
        self._playlists.append(playlist)

    def record_session(self, session) -> None:
        self._sessions.append(session)
        session.user.add_session(session)

    # ---------- Accessors ----------

    def get_track(self, track_id: str):
        for track in self._tracks:
            if track.track_id == track_id:
                return track
        return None

    def get_user(self, user_id: str):
        for user in self._users:
            if user.user_id == user_id:
                return user
        return None

    def get_artist(self, artist_id: str):
        for artist in self._artists:
            if artist.artist_id == artist_id:
                return artist
        return None

    def get_album(self, album_id: str):
        for album in self._albums:
            if album.album_id == album_id:
                return album
        return None

    def all_users(self):
        return list(self._users)

    def all_tracks(self):
        return list(self._tracks)

    def total_listening_time_minutes(self, start: datetime, end: datetime) -> float:
        total_seconds = 0

        for session in self._sessions:
            if start <= session.timestamp <= end:
                total_seconds += session.duration_listened_seconds

        return total_seconds / 60

    def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
        premium_users = [user for user in self._users if isinstance(user, PremiumUser)]
        # premium_users = [user for user in self._users if type(user) is PremiumUser]

        if not premium_users:
            return 0.0

        cutoff = datetime.now() - timedelta(days=days)
        total_unique_track_counts = 0

        for user in premium_users:
            unique_track_ids = set()

            for session in user.sessions:
                if session.timestamp >= cutoff:
                    unique_track_ids.add(session.track.track_id)

            total_unique_track_counts += len(unique_track_ids)

        return total_unique_track_counts / len(premium_users)

    def track_with_most_distinct_listeners(self):
        if not self._sessions:
            return None

        listeners_per_track = {}

        for session in self._sessions:
            track = session.track
            user = session.user

            if track.track_id not in listeners_per_track:
                listeners_per_track[track.track_id] = {
                    "track": track,
                    "listeners": set(),
                }

            listeners_per_track[track.track_id]["listeners"].add(user.user_id)

        best_track = None
        best_listener_count = -1

        for entry in listeners_per_track.values():
            listener_count = len(entry["listeners"])
            if listener_count > best_listener_count:
                best_listener_count = listener_count
                best_track = entry["track"]

        return best_track
