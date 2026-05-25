from fastapi import APIRouter

from app.api import auth, health, incidents, places, privacy, routes, safety, sos, users

api_router = APIRouter()

# Include specific application sub-routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/me", tags=["Users & Profile"])
api_router.include_router(safety.router, prefix="/safety", tags=["Safety & Risk Analysis"])
api_router.include_router(places.router)
api_router.include_router(routes.router)
api_router.include_router(incidents.router)
api_router.include_router(sos.router)
api_router.include_router(privacy.router)
