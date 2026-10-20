# Importa todos los modelos para que Base.metadata los conozca (Alembic autogenerate).
from entrevecinos.infrastructure.db.models.community import (
    CommunityMembershipModel,
    CommunityModel,
)
from entrevecinos.infrastructure.db.models.user import UserModel

__all__ = ["CommunityMembershipModel", "CommunityModel", "UserModel"]
