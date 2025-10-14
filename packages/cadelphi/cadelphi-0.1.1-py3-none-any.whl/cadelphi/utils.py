from __future__ import annotations

import random
import random
from typing import List, Optional, Sequence, Set

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from .models import Argument, SelectionStrategy, Vote

POSITIVE_THRESHOLD = 4
NEGATIVE_THRESHOLD = 2


def _candidate_ids(session: Session, stmt: Select[int]) -> List[int]:
    return [row[0] for row in session.execute(stmt).all()]


def _random_argument(
    session: Session, topic_id: int, exclude_ids: Set[int], exclude_authors: Optional[Sequence[int]] = None
) -> Optional[int]:
    stmt = select(Argument.id).where(Argument.topic_id == topic_id)
    if exclude_ids:
        stmt = stmt.where(~Argument.id.in_(exclude_ids))
    if exclude_authors:
        stmt = stmt.where(~Argument.author_id.in_(exclude_authors))
    ids = _candidate_ids(session, stmt)
    if not ids:
        return None
    return random.choice(ids)


def _related_arguments(
    session: Session,
    topic_id: int,
    origin_argument_id: int,
    threshold: int,
    comparison: str,
    exclude_ids: Set[int],
) -> List[int]:
    voter_stmt = select(Vote.participant_id).where(Vote.argument_id == origin_argument_id)
    if comparison == "gte":
        voter_stmt = voter_stmt.where(Vote.score >= threshold)
    else:
        voter_stmt = voter_stmt.where(Vote.score <= threshold)
    voters = [row[0] for row in session.execute(voter_stmt).all()]
    if not voters:
        return []

    vote_stmt = select(Vote.argument_id).where(Vote.participant_id.in_(voters))
    if comparison == "gte":
        vote_stmt = vote_stmt.where(Vote.score >= threshold)
    else:
        vote_stmt = vote_stmt.where(Vote.score <= threshold)
    vote_stmt = vote_stmt.where(Vote.argument_id != origin_argument_id)
    if exclude_ids:
        vote_stmt = vote_stmt.where(~Vote.argument_id.in_(exclude_ids))
    argument_ids = _candidate_ids(session, vote_stmt)
    if not argument_ids:
        return []

    stmt = select(Argument.id).where(Argument.id.in_(argument_ids), Argument.topic_id == topic_id)
    if exclude_ids:
        stmt = stmt.where(~Argument.id.in_(exclude_ids))
    return _candidate_ids(session, stmt)


def generate_argument_sequence(
    session: Session,
    topic_id: int,
    strategy: SelectionStrategy,
    *,
    participant_id: Optional[int] = None,
    steps: int = 3,
) -> List[int]:
    exclude_authors: Optional[List[int]] = None
    if participant_id:
        exclude_authors = [participant_id]
    selected: List[int] = []

    def pick_random() -> Optional[int]:
        return _random_argument(session, topic_id, set(selected), exclude_authors)

    first = pick_random()
    if first is None:
        return selected
    selected.append(first)

    while len(selected) < steps:
        if strategy == SelectionStrategy.RANDOM:
            next_arg = pick_random()
        elif strategy == SelectionStrategy.POSITIVE:
            origin = selected[-1]
            candidates = _related_arguments(
                session,
                topic_id,
                origin,
                POSITIVE_THRESHOLD,
                "gte",
                set(selected),
            )
            next_arg = random.choice(candidates) if candidates else pick_random()
        elif strategy == SelectionStrategy.NEGATIVE:
            origin = selected[-1]
            candidates = _related_arguments(
                session,
                topic_id,
                origin,
                NEGATIVE_THRESHOLD,
                "lte",
                set(selected),
            )
            next_arg = random.choice(candidates) if candidates else pick_random()
        else:
            next_arg = pick_random()

        if next_arg is None:
            break
        selected.append(next_arg)

    return selected[:steps]
