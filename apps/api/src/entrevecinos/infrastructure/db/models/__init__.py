# Importa todos los modelos para que Base.metadata los conozca (Alembic autogenerate).
from entrevecinos.infrastructure.db.models.user import UserModel

__all__ = ["UserModel"]
