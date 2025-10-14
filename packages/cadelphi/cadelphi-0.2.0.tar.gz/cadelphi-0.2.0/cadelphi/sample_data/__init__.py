"""Sample data loaders for cadelphi."""
from __future__ import annotations

from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import AdminSettings, SelectionStrategy, Topic
from ..security import hash_password
from .english import load_english_samples
from .turkish import load_turkish_samples


def load_sample_data(session: Session) -> None:
    """Populate the database with multilingual seed data if empty."""
    if session.scalar(select(func.count(Topic.id))) == 0:
        for loader in _sample_loaders():
            loader(session)
    ensure_admin_account(session)


def _sample_loaders() -> Iterable:
    return (load_english_samples, load_turkish_samples)


def ensure_admin_account(session: Session) -> None:
    """Create the default admin account when it is missing.

    Previous runs of the application may have already created the admin
    credentials.  In that case we skip inserting a new record to avoid
    violating the unique constraint on the ``admin_username`` column while
    preserving any custom password or settings that the administrator might
    have configured through the UI.
    """

    existing_admin = session.execute(
        select(AdminSettings).where(AdminSettings.admin_username == "admin")
    ).scalar_one_or_none()

    if not existing_admin:
        session.add(
            AdminSettings(
                admin_username="admin",
                password_hash=hash_password("password"),
                selection_strategy=SelectionStrategy.RANDOM,
            )
        )
