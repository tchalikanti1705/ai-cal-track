"""
Nutrition Routes
Food logging and nutrition tracking
"""
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.logging_config import get_logger
from app.services.nutrition_service import NutritionService
from app.models.nutrition import MealType
from app.schemas.nutrition import (
    FoodEntryCreate, FoodEntryResponse, FoodSearch,
    NutritionLogCreate, NutritionLogUpdate, NutritionLogResponse,
    QuickAddCalories, DailySummaryResponse, WeeklySummaryResponse, MacroBreakdown
)
from app.schemas.common import DataResponse, ListResponse, MessageResponse
from app.api.deps import get_current_user
from app.models.user import User

logger = get_logger(__name__)
router = APIRouter()


# ============ Food Database Routes ============

@router.get("/foods/search", response_model=ListResponse[FoodEntryResponse])
async def search_foods(
    query: str = Query(..., min_length=1),
    category: Optional[str] = None,
    limit: int = Query(default=20, le=50),
    db: Session = Depends(get_db)
):
    """
    Search food database
    """
    nutrition_service = NutritionService(db)
    foods = nutrition_service.search_foods(query, category, limit)
    
    return ListResponse(
        data=foods,
        total=len(foods)
    )


@router.get("/foods/{food_id}", response_model=DataResponse[FoodEntryResponse])
async def get_food(
    food_id: int,
    db: Session = Depends(get_db)
):
    """
    Get food entry by ID
    """
    nutrition_service = NutritionService(db)
    food = nutrition_service.get_food_by_id(food_id)
    
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found"
        )
    
    return DataResponse(data=food)


@router.get("/foods/barcode/{barcode}", response_model=DataResponse[FoodEntryResponse])
async def get_food_by_barcode(
    barcode: str,
    db: Session = Depends(get_db)
):
    """
    Get food entry by barcode
    """
    nutrition_service = NutritionService(db)
    food = nutrition_service.get_food_by_barcode(barcode)
    
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found for barcode"
        )
    
    return DataResponse(data=food)


@router.post("/foods", response_model=DataResponse[FoodEntryResponse])
async def create_food(
    data: FoodEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create custom food entry
    """
    nutrition_service = NutritionService(db)
    food = nutrition_service.create_food_entry(data)
    
    return DataResponse(data=food, message="Food entry created")


# ============ Nutrition Log Routes ============

@router.post("/log", response_model=DataResponse[NutritionLogResponse])
async def log_food(
    data: NutritionLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log food consumption
    """
    nutrition_service = NutritionService(db)
    log = nutrition_service.log_food(current_user.id, data)
    
    return DataResponse(data=log, message="Food logged successfully")


@router.post("/log/quick-add", response_model=DataResponse[NutritionLogResponse])
async def quick_add_calories(
    data: QuickAddCalories,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick add calories without full food details
    """
    nutrition_service = NutritionService(db)
    log = nutrition_service.quick_add_calories(
        current_user.id,
        data.log_date,
        data.meal_type,
        data.calories,
        data.name
    )
    
    return DataResponse(data=log)


@router.get("/log/{log_id}", response_model=DataResponse[NutritionLogResponse])
async def get_nutrition_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific nutrition log
    """
    nutrition_service = NutritionService(db)
    log = nutrition_service.get_nutrition_log(log_id, current_user.id)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )
    
    return DataResponse(data=log)


@router.patch("/log/{log_id}", response_model=DataResponse[NutritionLogResponse])
async def update_nutrition_log(
    log_id: int,
    data: NutritionLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update nutrition log
    """
    nutrition_service = NutritionService(db)
    log = nutrition_service.update_nutrition_log(log_id, current_user.id, data)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )
    
    return DataResponse(data=log)


@router.delete("/log/{log_id}", response_model=MessageResponse)
async def delete_nutrition_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete nutrition log
    """
    nutrition_service = NutritionService(db)
    success = nutrition_service.delete_nutrition_log(log_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )
    
    return MessageResponse(message="Log deleted")


@router.get("/logs/date/{log_date}", response_model=ListResponse[NutritionLogResponse])
async def get_logs_by_date(
    log_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all nutrition logs for a date
    """
    nutrition_service = NutritionService(db)
    logs = nutrition_service.get_logs_by_date(current_user.id, log_date)
    
    return ListResponse(data=logs, total=len(logs))


@router.get("/logs/meal/{log_date}/{meal_type}", response_model=ListResponse[NutritionLogResponse])
async def get_logs_by_meal(
    log_date: date,
    meal_type: MealType,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get nutrition logs for specific meal
    """
    nutrition_service = NutritionService(db)
    logs = nutrition_service.get_logs_by_meal(current_user.id, log_date, meal_type)
    
    return ListResponse(data=logs, total=len(logs))


# ============ Summary Routes ============

@router.get("/summary/daily/{summary_date}", response_model=DataResponse[DailySummaryResponse])
async def get_daily_summary(
    summary_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily nutrition summary
    """
    nutrition_service = NutritionService(db)
    summary = nutrition_service.get_daily_summary(current_user.id, summary_date)
    
    return DataResponse(data=summary)


@router.get("/summary/weekly/{start_date}", response_model=DataResponse[WeeklySummaryResponse])
async def get_weekly_summary(
    start_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly nutrition summary
    """
    nutrition_service = NutritionService(db)
    summary = nutrition_service.get_weekly_summary(current_user.id, start_date)
    
    return DataResponse(data=summary)


@router.get("/macros/{log_date}", response_model=DataResponse[MacroBreakdown])
async def get_macro_breakdown(
    log_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get macronutrient breakdown for a day
    """
    nutrition_service = NutritionService(db)
    breakdown = nutrition_service.get_macro_breakdown(current_user.id, log_date)
    
    return DataResponse(data=breakdown)
