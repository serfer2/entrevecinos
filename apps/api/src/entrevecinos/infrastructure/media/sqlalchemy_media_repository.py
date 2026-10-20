import uuid

from sqlalchemy import exists, select, true
from sqlalchemy.orm import Session

from entrevecinos.domain.media.entities import MediaAsset, NewMediaAsset
from entrevecinos.infrastructure.db.models import ListingImageModel, MediaAssetModel


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

    def owned_available(
        self, asset_ids: list[uuid.UUID], user_id: uuid.UUID, listing_id: uuid.UUID | None = None
    ) -> bool:
        ids = set(asset_ids)
        in_other_listing = exists().where(
            ListingImageModel.asset_id == MediaAssetModel.id,
            ListingImageModel.listing_id != listing_id if listing_id else true(),
        )
        valid = self._session.scalars(
            select(MediaAssetModel.id).where(
                MediaAssetModel.id.in_(ids),
                MediaAssetModel.uploaded_by == user_id,
                ~in_other_listing,
            )
        ).all()
        return set(valid) == ids

    def listing_using(self, asset_id: uuid.UUID) -> uuid.UUID | None:
        return self._session.scalar(
            select(ListingImageModel.listing_id).where(ListingImageModel.asset_id == asset_id)
        )
