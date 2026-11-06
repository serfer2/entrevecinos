import uuid

import pytest
import yaml
from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import CommunityMembershipModel
from tests.api_helpers import (
    contract_dir,
    create_community,
    join,
    publish_ok,
    register,
    request_access,
)

OWNER_EMAIL = "anunciante@example.com"
OWNER_PHONE = "600123456"


@pytest.fixture
def admin(client: TestClient) -> dict:
    return register(client, "admin@example.com")


@pytest.fixture
def community(client: TestClient, admin: dict) -> dict:
    return create_community(client, admin)


@pytest.fixture
def owner(client: TestClient, admin: dict, community: dict) -> dict:
    account = register(client, OWNER_EMAIL, full_name="Ana Anunciante", phone=OWNER_PHONE)
    join(client, admin, account, community["id"])
    return account


@pytest.mark.db
def test_members_get_phone_and_email(
    client: TestClient, admin: dict, owner: dict, community: dict
) -> None:
    listing = publish_ok(client, owner, community["id"])

    detail = client.get(f"/v1/listings/{listing['id']}", headers=admin["headers"]).json()
    listed = client.get(
        f"/v1/communities/{community['id']}/listings", headers=admin["headers"]
    ).json()

    assert detail["owner"]["email"] == OWNER_EMAIL
    assert detail["owner"]["phone"] == OWNER_PHONE
    assert listed["items"][0]["owner"] == detail["owner"]


@pytest.mark.db
def test_owner_without_phone_keeps_email(
    client: TestClient, admin: dict, owner: dict, community: dict
) -> None:
    client.patch("/v1/users/me", json={"phone": None}, headers=owner["headers"])
    listing = publish_ok(client, owner, community["id"])

    detail = client.get(f"/v1/listings/{listing['id']}", headers=admin["headers"]).json()

    assert (detail["owner"]["phone"], detail["owner"]["email"]) == (None, OWNER_EMAIL)


@pytest.mark.db
@pytest.mark.parametrize("status", ["pending", "rejected", "blocked", None])
def test_contact_data_never_reaches_non_members(
    client: TestClient,
    owner: dict,
    community: dict,
    db_session: Session,
    status: str | None,
) -> None:
    listing = publish_ok(client, owner, community["id"])
    other = register(client, "otro@example.com")
    if status is not None:
        request_access(client, other, community["id"])
        db_session.execute(
            update(CommunityMembershipModel)
            .where(
                CommunityMembershipModel.community_id == uuid.UUID(community["id"]),
                CommunityMembershipModel.user_id == uuid.UUID(other["user"]["id"]),
            )
            .values(status=status)
        )

    responses = [
        client.get(f"/v1/listings/{listing['id']}", headers=other["headers"]),
        client.get(f"/v1/communities/{community['id']}/listings", headers=other["headers"]),
        client.get(f"/v1/listings/{listing['id']}"),
    ]

    assert [r.status_code for r in responses] == [403, 403, 401]
    for response in responses:
        assert OWNER_EMAIL not in response.text and OWNER_PHONE not in response.text


def test_owner_schema_matches_the_contract(client: TestClient) -> None:
    docs = contract_dir()
    if docs is None:
        pytest.skip("docs/api no está disponible (en Compose se monta en /docs/api)")
    contract = yaml.safe_load((docs / "components" / "schemas" / "ListingOwner.yaml").read_text())
    generated = client.app.openapi()["components"]["schemas"]["ListingOwnerResponse"]

    assert set(generated["properties"]) == set(contract["properties"])
    assert set(generated["required"]) >= set(contract["required"])
    assert "email" in generated["required"]
