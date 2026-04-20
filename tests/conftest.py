"""
conftest.py
-----------
Shared pytest fixtures used by both the public and private test suites.
"""

import pytest
from datetime import date, datetime, timedelta

from streaming.platform import StreamingPlatform
from streaming.artists import Artist
from streaming.albums import Album
from streaming.tracks import (
    AlbumTrack,
    SingleRelease,
    InterviewEpisode,
    NarrativeEpisode,
    AudiobookTrack,
)
from streaming.users import FreeUser, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.sessions import ListeningSession
from streaming.playlists import Playlist, CollaborativePlaylist


# ---------------------------------------------------------------------------
# Helper - timestamps relative to the real current time so that the
# "last 30 days" window in Q2 always contains RECENT sessions.
# ---------------------------------------------------------------------------
FIXED_NOW = datetime.now().replace(microsecond=0)
RECENT = FIXED_NOW - timedelta(days=10)   # well within 30-day window
OLD    = FIXED_NOW - timedelta(days=60)   # outside 30-day window


@pytest.fixture
def platform() -> StreamingPlatform:
    """Return a fully populated StreamingPlatform instance."""
    platform = StreamingPlatform("TestStream")

    # ------------------------------------------------------------------
    # Artists
    # ------------------------------------------------------------------
    pixels = Artist("a1", "Pixels", genre="pop")
    platform.add_artist(pixels)

    # ------------------------------------------------------------------
    # Albums & AlbumTracks
    # ------------------------------------------------------------------
    dd = Album("alb1", "Digital Dreams", artist=pixels, release_year=2022)
    t1 = AlbumTrack("t1", "Pixel Rain",    180, "pop", pixels, track_number=1)
    t2 = AlbumTrack("t2", "Grid Horizon",  210, "pop", pixels, track_number=2)
    t3 = AlbumTrack("t3", "Vector Fields", 195, "pop", pixels, track_number=3)
    for track in (t1, t2, t3):
        dd.add_track(track)
        platform.add_track(track)
        pixels.add_track(track)
    platform.add_album(dd)

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    alice = FreeUser("u1", "Alice", age=30)
    bob   = PremiumUser("u2", "Bob", age=25, subscription_start=date(2023, 1, 1))
    carol = FamilyAccountUser("u3", "Carol", age=40)
    dave  = FamilyMember("u4", "Dave", age=15, parent=carol)
    carol.add_sub_user(dave)

    for user in (alice, bob, carol, dave):
        platform.add_user(user)

    # ------------------------------------------------------------------
    # Sessions (all at RECENT timestamp, well within the 30-day window)
    #
    # alice listens to t1 (120s), t2 (180s), t3 (195s)  -> completes "Digital Dreams"
    # bob   listens to t1 (300s)
    # dave  listens to t1 (90s)  -> underage FamilyMember (age=15)
    #
    # Totals used in tests:
    #   Q1  all sessions: 120+180+195+300+90 = 885s = 14.75 min
    #   Q2  bob unique tracks in 30d: {t1} -> avg = 1.0
    #   Q3  t1 distinct listeners: alice+bob+dave = 3  (most of all tracks)
    #   Q4  FreeUser avg: 495/3=165.0  PremiumUser avg: 300.0  FamilyMember avg: 90.0
    #   Q5  dave (age 15 < 18): 90s = 1.5 min
    #   Q6  pixels total: 885s = 14.75 min
    #   Q7  alice: all pop -> ("pop", 100.0)
    #   Q10 alice completed "Digital Dreams"
    # ------------------------------------------------------------------
    sessions = [
        ListeningSession("s1", alice, t1, RECENT, 120),
        ListeningSession("s2", alice, t2, RECENT, 180),
        ListeningSession("s3", alice, t3, RECENT, 195),
        ListeningSession("s4", bob,   t1, RECENT, 300),
        ListeningSession("s5", dave,  t1, RECENT, 90),
    ]
    for session in sessions:
        platform.record_session(session)

    # ------------------------------------------------------------------
    # Playlists
    #   pl1  – standard Playlist  with 2 tracks  (t1, t2)
    #   cpl1 – CollaborativePlaylist with 3 tracks (t1, t2, t3)
    #
    # Q9  Playlist avg: 2.0   CollaborativePlaylist avg: 3.0
    # ------------------------------------------------------------------
    pl1 = Playlist("pl1", "Alice Faves", owner=alice)
    pl1.add_track(t1)
    pl1.add_track(t2)
    platform.add_playlist(pl1)

    cpl1 = CollaborativePlaylist("cpl1", "Collab Mix", owner=alice)
    cpl1.add_track(t1)
    cpl1.add_track(t2)
    cpl1.add_track(t3)
    platform.add_playlist(cpl1)

    return platform


@pytest.fixture
def fixed_now() -> datetime:
    """Expose the shared FIXED_NOW constant to tests."""
    return FIXED_NOW


@pytest.fixture
def recent_ts() -> datetime:
    return RECENT


@pytest.fixture
def old_ts() -> datetime:
    return OLD
