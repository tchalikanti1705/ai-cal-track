# API routes module
from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .nutrition import router as nutrition_router
from .exercise import router as exercise_router
from .water import router as water_router
from .walking import router as walking_router
from .food_scan import router as food_scan_router
from .insights import router as insights_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(nutrition_router, prefix="/nutrition", tags=["Nutrition"])
api_router.include_router(exercise_router, prefix="/exercise", tags=["Exercise"])
api_router.include_router(water_router, prefix="/water", tags=["Water"])
api_router.include_router(walking_router, prefix="/walking", tags=["Walking"])
api_router.include_router(food_scan_router, prefix="/food-scan", tags=["Food Scanning"])
api_router.include_router(insights_router, prefix="/insights", tags=["Insights"])
