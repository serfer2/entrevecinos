import uuid

from sqlalchemy import exists, or_, select
from sqlalchemy.orm import Session

from entrevecinos.domain.communities.entities import MembershipRole, MembershipStatus
from entrevecinos.domain.media.entities import MediaAsset, NewMediaAsset
from entrevecinos.infrastructure.db.models import (
    CommunityMembershipModel,
    ListingImageModel,
    ListingModel,
    MediaAssetModel,
)

VISIBLE_STATUSES = ("active", "reserved", "completed")


def to_domain(model: MediaAssetModel) -> MediaAsset:
    return MediaAsset(
        id=model.id,
        uploaded_by=model.uploaded_by,
        object_key=model.object_key,
        mime_type=model.mime_type,
        size_bytes=model.size_bytes,
        created_at=model.created_at,
    )


class SqlAlchemyMediaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, asset: NewMediaAsset) -> MediaAsset:
        model = MediaAssetModel(
            uploaded_by=asset.uploaded_by,
            object_key=asset.object_key,
            mime_type=asset.mime_type,
            size_bytes=asset.size_bytes,
            sha256=asset.sha256,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return to_domain(model)

    def get(self, asset_id: uuid.UUID) -> MediaAsset | None:
        model = self._session.get(MediaAssetModel, asset_id)
        return to_domain(model) if model else None

    def is_readable_by(self, asset_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        membership = CommunityMembershipModel
        query = (
            select(ListingImageModel.asset_id)
            .join(ListingModel, ListingModel.id == ListingImageModel.listing_id)
            .join(
                membership,
                (membership.community_id == ListingModel.community_id)
                & (membership.user_id == user_id)
                & (membership.status == MembershipStatus.APPROVED),
            )
            .where(
                ListingImageModel.asset_id == asset_id,
                ListingModel.deleted_at.is_(None),
                or_(
                    ListingModel.status.in_(VISIBLE_STATUSES),
                    # Un anuncio retirado solo lo ven su autor y los gestores de la comunidad.
                    (ListingModel.status == "hidden")
                    & (
                        (ListingModel.owner_id == user_id)
                        | membership.role.in_(
                            [MembershipRole.COMMUNITY_ADMIN, MembershipRole.MODERATOR]
                        )
                    ),
                ),
            )
        )
        return bool(self._session.scalar(select(exists(query))))
