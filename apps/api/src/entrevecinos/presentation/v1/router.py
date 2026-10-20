from fastapi import APIRouter

from entrevecinos.presentation.v1 import auth, communities, media, users

router = APIRouter(prefix="/v1")
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(communities.router)
router.include_router(media.router)
