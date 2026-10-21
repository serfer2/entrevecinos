# Importa todos los modelos para que Base.metadata los conozca (Alembic autogenerate).
from entrevecinos.infrastructure.db.models.community import (
    CommunityMembershipModel,
    CommunityModel,
)
from entrevecinos.infrastructure.db.models.listing import (
    CategoryModel,
    ListingImageModel,
    ListingModel,
    MediaAssetModel,
)
from entrevecinos.infrastructure.db.models.user import EmailVerificationModel, UserModel

__all__ = [
    "CategoryModel",
    "CommunityMembershipModel",
    "CommunityModel",
    "EmailVerificationModel",
    "ListingImageModel",
    "ListingModel",
    "MediaAssetModel",
    "UserModel",
]
