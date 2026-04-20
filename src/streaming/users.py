"""
users.py
--------
Implement the class hierarchy for platform users.

Classes to implement:
  - User (base class)
    - FreeUser
    - PremiumUser
    - FamilyAccountUser
    - FamilyMember
"""
from __future__ import annotations

from datetime import date


class User:
    """Base class for all platform users."""

    def __init__(self, user_id: str, name: str, age: int) -> None:
        self.user_id = user_id
        self.name = name
        self.age = age
        self.sessions = []

    def add_session(self, session) -> None:
        self.sessions.append(session)

    def total_listening_seconds(self) -> int:
        return sum(session.duration_listened_seconds for session in self.sessions)

    def total_listening_minutes(self) -> float:
        return self.total_listening_seconds() / 60

    def unique_tracks_listened(self) -> set[str]:
        return {session.track.track_id for session in self.sessions}


class FreeUser(User):
    """User with free-tier access and no subscription."""
    pass


class PremiumUser(User):
    """Paying user with a subscription start date."""

    def __init__(self, user_id: str, name: str, age: int, subscription_start: date) -> None:
        super().__init__(user_id, name, age)
        self.subscription_start = subscription_start


class FamilyAccountUser(PremiumUser):
    """Premium user who manages a family account with sub-users."""

    def __init__(
            self,
            user_id: str,
            name: str,
            age: int,
            subscription_start: date | None = None,
    ) -> None:
        if subscription_start is None:
            subscription_start = date.today()
        super().__init__(user_id, name, age, subscription_start)
        self.sub_users = []

    def add_sub_user(self, member) -> None:
        self.sub_users.append(member)

    def all_members(self) -> list[User]:
        return [self] + self.sub_users


class FamilyMember(User):
    """Sub-user belonging to a FamilyAccountUser."""

    def __init__(self, user_id: str, name: str, age: int, parent: FamilyAccountUser) -> None:
        super().__init__(user_id, name, age)
        self.parent = parent
