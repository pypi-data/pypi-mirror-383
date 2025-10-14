from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import AdminSettings, Argument, Participant, SelectionStrategy, Topic, Vote
from .security import hash_password


def load_sample_data(session: Session) -> None:
    if session.scalar(select(func.count(Topic.id))) > 0:
        ensure_admin_account(session)
        return

    participants = [
        Participant(name="Ayşe"),
        Participant(name="Mehmet"),
        Participant(name="Leyla"),
        Participant(name="Can"),
    ]
    session.add_all(participants)
    session.flush()

    sustainability = Topic(
        title="Sürdürülebilir Şehir Planlaması",
        description="Enerji verimliliği ve yaşam kalitesini artırmak için öneriler",
    )
    ai_ethics = Topic(
        title="Yapay Zeka Etiği",
        description="Yapay zekanın karar alma süreçlerinde şeffaflık ve hesap verebilirlik",
    )
    session.add_all([sustainability, ai_ethics])
    session.flush()

    arguments = [
        Argument(
            topic_id=sustainability.id,
            author_id=participants[0].id,
            content="Toplu taşımayı cazip hale getirmek için kent içi mikro mobilite ağları kurulmalı.",
        ),
        Argument(
            topic_id=sustainability.id,
            author_id=participants[1].id,
            content="Yeni binalarda pasif enerji standartları zorunlu olmalı.",
        ),
        Argument(
            topic_id=sustainability.id,
            author_id=participants[2].id,
            content="Yağmur suyu hasadı altyapısı belediye yatırımıyla desteklenmeli.",
        ),
        Argument(
            topic_id=ai_ethics.id,
            author_id=participants[3].id,
            content="Algoritmik karar destek sistemleri için bağımsız etik denetimler yapılmalı.",
        ),
        Argument(
            topic_id=ai_ethics.id,
            author_id=participants[0].id,
            content="Model eğitimi sırasında kullanılan veriler anonimleştirilmeli ve kamuya açıklanmalı.",
        ),
        Argument(
            topic_id=ai_ethics.id,
            author_id=participants[1].id,
            content="Kritik kararları etkileyen modellerde açıklanabilirlik raporu zorunlu hale getirilmeli.",
        ),
    ]
    session.add_all(arguments)
    session.flush()

    votes = [
        Vote(
            argument_id=arguments[0].id,
            participant_id=participants[1].id,
            score=5,
            comment="Ulaşım entegrasyonu için harika bir çözüm.",
        ),
        Vote(
            argument_id=arguments[0].id,
            participant_id=participants[2].id,
            score=4,
            comment="Bisiklet yollarıyla desteklenirse etkili olur.",
        ),
        Vote(
            argument_id=arguments[1].id,
            participant_id=participants[0].id,
            score=4,
            comment="Başlangıç maliyeti yüksek olabilir.",
        ),
        Vote(
            argument_id=arguments[1].id,
            participant_id=participants[2].id,
            score=2,
            comment="Müteahhitler için zorlayıcı olabilir.",
        ),
        Vote(argument_id=arguments[2].id, participant_id=participants[3].id, score=3, comment="Su yönetimi açısından mantıklı."),
        Vote(argument_id=arguments[3].id, participant_id=participants[0].id, score=5, comment="Bağımsız denetim güven sağlar."),
        Vote(argument_id=arguments[4].id, participant_id=participants[3].id, score=4, comment="Veri koruması için gerekli."),
        Vote(argument_id=arguments[4].id, participant_id=participants[1].id, score=1, comment="Tam şeffaflık rekabeti zedeleyebilir."),
        Vote(argument_id=arguments[5].id, participant_id=participants[0].id, score=5, comment="Kararların gerekçesi kamuya açık olmalı."),
        Vote(argument_id=arguments[5].id, participant_id=participants[2].id, score=4, comment="Güven tesis etmek için önemli."),
    ]
    session.add_all(votes)

    ensure_admin_account(session)


def ensure_admin_account(session: Session) -> None:
    if session.scalar(select(func.count(AdminSettings.id))) == 0:
        session.add(
            AdminSettings(
                admin_username="admin",
                password_hash=hash_password("password"),
                selection_strategy=SelectionStrategy.RANDOM,
            )
        )
