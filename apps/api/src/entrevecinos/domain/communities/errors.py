from entrevecinos.domain.errors import NotFoundError


class CommunityNotFound(NotFoundError):
    """La comunidad no existe o está desactivada."""
