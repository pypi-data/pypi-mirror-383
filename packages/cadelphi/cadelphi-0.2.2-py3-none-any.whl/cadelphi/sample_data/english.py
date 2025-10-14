"""English sample records for cadelphi."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Argument, Participant, Topic, Vote


def load_english_samples(session: Session) -> None:
    """Seed the database with English demonstration data if missing."""
    if session.scalar(select(Topic.id).where(Topic.title == "Sustainable Urban Planning")):
        return

    participants = [
        Participant(name="Alice"),
        Participant(name="Bob"),
        Participant(name="Chloe"),
        Participant(name="Diego"),
    ]
    session.add_all(participants)
    session.flush()

    sustainable = Topic(
        title="Sustainable Urban Planning",
        description="Ideas to increase energy efficiency and livability in metropolitan areas.",
    )
    ai_ethics = Topic(
        title="Artificial Intelligence Governance",
        description="Approaches to keep automated decision making accountable and transparent.",
    )
    session.add_all([sustainable, ai_ethics])
    session.flush()

    arguments = [
        Argument(
            topic_id=sustainable.id,
            author_id=participants[0].id,
            content="Create dedicated micro-mobility corridors that connect major transit hubs.",
        ),
        Argument(
            topic_id=sustainable.id,
            author_id=participants[1].id,
            content="Require passive house standards for new municipal housing developments.",
        ),
        Argument(
            topic_id=sustainable.id,
            author_id=participants[2].id,
            content="Fund rainwater harvesting infrastructure across public buildings.",
        ),
        Argument(
            topic_id=ai_ethics.id,
            author_id=participants[3].id,
            content="Mandate independent ethics audits for algorithmic decision support systems.",
        ),
        Argument(
            topic_id=ai_ethics.id,
            author_id=participants[0].id,
            content="Publish anonymised training data summaries for high-impact AI services.",
        ),
        Argument(
            topic_id=ai_ethics.id,
            author_id=participants[1].id,
            content="Require explainability reports for automated systems that influence critical outcomes.",
        ),
    ]
    session.add_all(arguments)
    session.flush()

    votes = [
        Vote(
            argument_id=arguments[0].id,
            participant_id=participants[1].id,
            score=5,
            comment="Great way to encourage multimodal transport.",
        ),
        Vote(
            argument_id=arguments[0].id,
            participant_id=participants[2].id,
            score=4,
            comment="Will need safe bike parking at every junction.",
        ),
        Vote(
            argument_id=arguments[1].id,
            participant_id=participants[0].id,
            score=4,
            comment="Upfront retrofitting costs could be challenging.",
        ),
        Vote(
            argument_id=arguments[1].id,
            participant_id=participants[2].id,
            score=2,
            comment="Developers may push back without subsidies.",
        ),
        Vote(
            argument_id=arguments[2].id,
            participant_id=participants[3].id,
            score=3,
            comment="Helps climate resilience but needs maintenance funding.",
        ),
        Vote(
            argument_id=arguments[3].id,
            participant_id=participants[0].id,
            score=5,
            comment="Independent audits would build trust.",
        ),
        Vote(
            argument_id=arguments[4].id,
            participant_id=participants[3].id,
            score=4,
            comment="Transparency is vital for data stewardship.",
        ),
        Vote(
            argument_id=arguments[4].id,
            participant_id=participants[1].id,
            score=1,
            comment="Full disclosure might expose proprietary insights.",
        ),
        Vote(
            argument_id=arguments[5].id,
            participant_id=participants[0].id,
            score=5,
            comment="Clear rationales keep affected communities informed.",
        ),
        Vote(
            argument_id=arguments[5].id,
            participant_id=participants[2].id,
            score=4,
            comment="Important step toward responsible deployment.",
        ),
    ]
    session.add_all(votes)
