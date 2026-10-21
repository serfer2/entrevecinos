from datetime import UTC, datetime

import pytest
from alembic import command
from sqlalchemy import Engine, func, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import (
    CommunityMembershipModel,
    CommunityModel,
    UserModel,
)
from tests.conftest import alembic_config

pytestmark = pytest.mark.db


def make_user(db_session: Session, email: str = "vecino@example.com") -> UserModel:
    user = UserModel(
        email=email, password_hash="hash", full_name="Alex Vecino", email_verified_at=func.now()
    )
    db_session.add(user)
    db_session.flush()
    return user


def make_community(db_session: Session, user: UserModel, **overrides: object) -> CommunityModel:
    community = CommunityModel(
        **{"name": "Urbanización Los Olivos", "created_by": user.id, **overrides}
    )
    db_session.add(community)
    db_session.flush()
    return community


def test_minimal_insert_applies_defaults(db_session: Session) -> None:
    user = make_user(db_session)
    community = make_community(db_session, user)
    membership = CommunityMembershipModel(community_id=community.id, user_id=user.id)
    db_session.add(membership)
    db_session.flush()
    db_session.refresh(community)
    db_session.refresh(membership)

    assert community.is_active is True
    assert community.created_at is not None
    assert (membership.role, membership.status) == ("member", "pending")
    assert membership.requested_at is not None
    assert membership.joined_at is None


def test_community_name_is_not_unique(db_session: Session) -> None:
    user = make_user(db_session)
    make_community(db_session, user, city="Madrid")
    make_community(db_session, user, city="Sevilla")


def test_duplicate_membership_is_rejected(db_session: Session) -> None:
    user = make_user(db_session)
    community = make_community(db_session, user)
    db_session.add(CommunityMembershipModel(community_id=community.id, user_id=user.id))
    db_session.flush()
    db_session.expunge_all()
    db_session.add(CommunityMembershipModel(community_id=community.id, user_id=user.id))

    with pytest.raises(IntegrityError, match="pk_community_membership"):
        db_session.flush()


def test_one_inactive_community_per_creator(db_session: Session) -> None:
    user = make_user(db_session)
    make_community(db_session, user, is_active=False)
    make_community(db_session, user, city="Madrid")
    make_community(db_session, user, city="Sevilla")

    with pytest.raises(IntegrityError, match="uq_community_one_pending_per_creator"):
        make_community(db_session, user, is_active=False)


@pytest.mark.parametrize("name", ["", "   "])
def test_blank_community_name_is_rejected(db_session: Session, name: str) -> None:
    user = make_user(db_session)

    with pytest.raises(IntegrityError, match="ck_community_name_not_blank"):
        make_community(db_session, user, name=name)


def test_approved_membership_requires_joined_at(db_session: Session) -> None:
    user = make_user(db_session)
    community = make_community(db_session, user)
    db_session.add(
        CommunityMembershipModel(community_id=community.id, user_id=user.id, status="approved")
    )

    with pytest.raises(IntegrityError, match="ck_community_membership_approved_has_joined_at"):
        db_session.flush()


def test_approved_membership_with_joined_at_is_accepted(db_session: Session) -> None:
    user = make_user(db_session)
    community = make_community(db_session, user)
    db_session.add(
        CommunityMembershipModel(
            community_id=community.id,
            user_id=user.id,
            role="community_admin",
            status="approved",
            joined_at=datetime.now(UTC),
        )
    )
    db_session.flush()


def test_migration_0002_is_reversible(db_engine: Engine) -> None:
    with db_engine.begin() as connection:
        command.downgrade(alembic_config(connection), "0001")
        assert not inspect(connection).has_table("community")
        assert inspect(connection).has_table("users")

    with db_engine.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
        assert inspect(connection).has_table("community_membership")


def test_migration_0007_is_reversible(db_engine: Engine) -> None:
    def indexes(connection) -> set[str]:
        return {index["name"] for index in inspect(connection).get_indexes("community")}

    with db_engine.begin() as connection:
        command.downgrade(alembic_config(connection), "0006")
        assert "uq_community_one_pending_per_creator" not in indexes(connection)

    with db_engine.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
        assert "uq_community_one_pending_per_creator" in indexes(connection)
