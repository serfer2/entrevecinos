from fastapi import APIRouter

from entrevecinos.presentation.v1 import auth, users

router = APIRouter(prefix="/v1")
router.include_router(auth.router)
router.include_router(users.router)
