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
from streaming.playlists import CollaborativePlaylist, Playlist
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

    # Q1: Calculate listening time in minutes
    def total_listening_time_minutes(self, start: datetime, end: datetime) -> float: # return type float
        total_seconds = 0 # for counting in seconds

        for session in self._sessions: # going through all sessions in self._sessions
            if start <= session.timestamp <= end: # only counting session, when timestamp ist bigger or equal to start
                # or timestamp is smaller or equal to end
                total_seconds += session.duration_listened_seconds # if session is in this window, we count it to the total

        return total_seconds / 60 # # convert total seconds to minutes (required output)

    # Q2: average of unique tracks listened to per premiumUser in the last days
    def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
        # premium_users = [user for user in self._users if isinstance(user, PremiumUser)]
        # premium_users = [user for user in self._users if type(user) is PremiumUser]

        # # filter only exact PremiumUser (exclude subclasses like FamilyAccountUser):
        premium_users =[]
        for user in self._users:
            if type(user) is PremiumUser:
                premium_users.append(user)

        if not premium_users: # When the list is empty (no premiumUser)
            return 0.0

        # we only want to count in sessions that are new
        cutoff = datetime.now() - timedelta(days=days) # We calculate the date that is "days" days in the past.
        total_unique_track_counts = 0

        for user in premium_users: # iterating through all premiumUsers (list we made)
            unique_track_ids = set() # A set does not save any duplicates

            for session in user.sessions: # only going through the sessions of the User for the one iteration
                if session.timestamp >= cutoff: # only counting in sessions that are newer or equal to the variable cutoff
                    unique_track_ids.add(session.track.track_id) # adding the trackID

            total_unique_track_counts += len(unique_track_ids) # count distinct tracks for this user

        return total_unique_track_counts / len(premium_users) # calculating the mean

    #Q3: # looking for track with the most distinct listeners
    def track_with_most_distinct_listeners(self): # no added parameters, just looking at all the sessions
        if not self._sessions: # if there is no session, then there is no listener
            return None

        listeners_per_track = {} # a dictionary that saves the track-object and its set of distinct listeners

        for session in self._sessions: # going through every session of the platform
            track = session.track
            user = session.user

            if track.track_id not in listeners_per_track: # if we have not already added the track to the dictionary:
                listeners_per_track[track.track_id] = {
                    "track": track,
                    "listeners": set(), # set so there are no duplicates
                } # we create a new entry for the track and his listeners
            # the User of the session will be the listener of the track:
            # We are doing this, so when the same User listens to a song track more than ones, his userID
            # will be added again and again, but in a set this is not possible
            listeners_per_track[track.track_id]["listeners"].add(user.user_id)

        best_track = None
        best_listener_count = -1 # -1 so the first real track will be the best track instantly

        for entry in listeners_per_track.values(): # iterating through all the entries in the dictionary
            listener_count = len(entry["listeners"]) # how many listeners are in the entry (How many listeners does the track have)?
            if listener_count > best_listener_count: # checking if the track we are currently iterating with is better than the previous
                # (update best track if current has more distinct listeners)
                best_listener_count = listener_count
                best_track = entry["track"]

        return best_track # gives back the track with the most listeners

    #Q4: average session duration for each user type, sorted from longest to shortest
    def avg_session_duration_by_user_type(self) -> list[tuple[str, float]]:
        grouped = {}

        # group all session durations by the exact user type name
        for session in self._sessions:
            type_name = type(session.user).__name__
            grouped.setdefault(type_name, []).append(session.duration_listened_seconds)

        result = []

        # make sure all expected user types are present, even if they have no sessions
        all_type_names = ["FreeUser", "PremiumUser", "FamilyAccountUser", "FamilyMember"]
        for type_name in all_type_names:
            durations = grouped.get(type_name, [])
            avg = sum(durations) / len(durations) if durations else 0.0
            result.append((type_name, avg))

        # sort by average duration descending
        result.sort(key=lambda item: item[1], reverse=True)
        return result

    #Q5: total listening time in minutes for underage family sub-users
    def total_listening_time_underage_sub_users_minutes(self, age_threshold: int = 18) -> float:
        total_seconds = 0

        # only FamilyMember sessions count, and only if the member is younger than the threshold
        for session in self._sessions:
            user = session.user
            if isinstance(user, FamilyMember) and user.age < age_threshold:
                total_seconds += session.duration_listened_seconds

        # convert total seconds to minutes
        return total_seconds / 60

    #6: top n artists ranked by total listening time of their songs
    def top_artists_by_listening_time(self, n: int = 5) -> list[tuple[object, float]]:
        listening_time = {}

        # only Song tracks count here
        for session in self._sessions:
            track = session.track
            if isinstance(track, Song):
                artist = track.artist
                listening_time[artist] = listening_time.get(artist, 0) + session.duration_listened_seconds

        # convert seconds to minutes for the final result
        result = [(artist, seconds / 60) for artist, seconds in listening_time.items()]

        # sort by listening time descending and return only the top n artists
        result.sort(key=lambda item: item[1], reverse=True)
        return result[:n]

    #Q7: return the most listened genre of a user and its percentage of total listening time
    def user_top_genre(self, user_id: str) -> tuple[str, float] | None:
        user = self.get_user(user_id)
        # return None if user does not exist or has no listening history
        if user is None or not user.sessions:
            return None

        genre_seconds = {}
        total_seconds = 0
        # accumulate listening time per genre
        for session in user.sessions:
            genre = session.track.genre
            seconds = session.duration_listened_seconds
            genre_seconds[genre] = genre_seconds.get(genre, 0) + seconds
            total_seconds += seconds

        # find genre with the highest listening time
        top_genre = None
        top_seconds = -1
        for genre, seconds in genre_seconds.items():
            if seconds > top_seconds:
                top_genre = genre
                top_seconds = seconds

        # calculate percentage of total listening time
        percentage = (top_seconds / total_seconds) * 100
        return (top_genre, percentage)

    #Q8: return all collaborative playlists with more than threshold distinct artists
    def collaborative_playlists_with_many_artists(
        self, threshold: int = 3
    ) -> list[CollaborativePlaylist]:
        result = []

        # check only CollaborativePlaylists
        for playlist in self._playlists:
            if isinstance(playlist, CollaborativePlaylist):
                artist_set = set()

                # count distinct artists (only Song tracks have artists)
                for track in playlist.tracks:
                    if isinstance(track, Song):
                        artist_set.add(track.artist)

                # include playlist if number of artists exceeds threshold
                if len(artist_set) > threshold:
                    result.append(playlist)

        return result

    #Q9: compute average number of tracks for each playlist type
    def avg_tracks_per_playlist_type(self) -> dict[str, float]:
        standard_playlists = [p for p in self._playlists if type(p) is Playlist]
        collaborative_playlists = [p for p in self._playlists if isinstance(p, CollaborativePlaylist)]

        # calculate averages (0.0 if no playlists of that type exist)
        standard_avg = (
            sum(len(p.tracks) for p in standard_playlists) / len(standard_playlists)
            if standard_playlists
            else 0.0
        )
        collaborative_avg = (
            sum(len(p.tracks) for p in collaborative_playlists) / len(collaborative_playlists)
            if collaborative_playlists
            else 0.0
        )

        return {
            "Playlist": standard_avg,
            "CollaborativePlaylist": collaborative_avg,
        }

    #Q10: return users who listened to every track of at least one album
    def users_who_completed_albums(self) -> list[tuple[object, list[str]]]:
        result = []

        for user in self._users:
            # collect all track IDs the user has listened to
            listened_track_ids = {session.track.track_id for session in user.sessions}
            completed_album_titles = []

            for album in self._albums:
                if not album.tracks:
                    continue

                album_track_ids = {track.track_id for track in album.tracks}

                # user completed album if all album tracks are in their listening history
                if album_track_ids.issubset(listened_track_ids):
                    completed_album_titles.append(album.title)

            # include user only if they completed at least one album
            if completed_album_titles:
                result.append((user, completed_album_titles))

        return result