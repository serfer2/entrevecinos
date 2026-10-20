import uuid
from dataclasses import dataclass
from decimal import Decimal

from entrevecinos.application.authorization.community_access import CommunityAccess
from entrevecinos.application.listings.ports import CategoryRepository, ListingRepository
from entrevecinos.application.media.ports import MediaRepository
from entrevecinos.domain.listings.entities import Listing, ListingType, NewListing, normalize_price
from entrevecinos.domain.listings.errors import InvalidCategory, InvalidImages
from entrevecinos.domain.users.entities import User


@dataclass(frozen=True, slots=True)
class PublishListingCommand:
    category_id: uuid.UUID
    title: str
    description: str
    type: ListingType
    price: Decimal | None = None
    currency: str | None = None
    image_asset_ids: tuple[uuid.UUID, ...] = ()


class PublishListing:
    def __init__(
        self,
        access: CommunityAccess,
        categories: CategoryRepository,
        media: MediaRepository,
        listings: ListingRepository,
    ) -> None:
        self._access = access
        self._categories = categories
        self._media = media
        self._listings = listings

    def execute(
        self, user: User, community_id: uuid.UUID, command: PublishListingCommand
    ) -> Listing:
        self._access.require_member(user, community_id)
        if not self._categories.is_active(command.category_id):
            raise InvalidCategory
        images = list(command.image_asset_ids)
        if images and not self._media.owned_available(images, user.id):
            raise InvalidImages
        price, currency = normalize_price(command.price, command.currency)
        return self._listings.add(
            NewListing(
                community_id=community_id,
                owner_id=user.id,
                category_id=command.category_id,
                title=command.title,
                description=command.description,
                type=command.type,
                price=price,
                currency=currency,
                image_asset_ids=tuple(images),
            )
        )
