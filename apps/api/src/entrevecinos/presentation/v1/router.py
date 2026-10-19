from fastapi import APIRouter

from entrevecinos.presentation.v1 import auth

router = APIRouter(prefix="/v1")
router.include_router(auth.router)
