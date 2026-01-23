"""
Food Scanning Routes
AI-powered food recognition
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.logging_config import get_logger
from app.services.food_scan_service import FoodScanService
from app.models.nutrition import MealType
from app.schemas.food_scan import (
    FoodScanFromImage, FoodScanFromBarcode,
    FoodScanResponse, ScanResultConfirm, ScanResultCorrect
)
from app.schemas.nutrition import NutritionLogResponse
from app.schemas.common import DataResponse, ListResponse, MessageResponse
from app.api.deps import get_current_user
from app.models.user import User

logger = get_logger(__name__)
router = APIRouter()


@router.post("/image", response_model=DataResponse[FoodScanResponse])
async def scan_food_image(
    data: FoodScanFromImage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scan food from image using AI
    """
    scan_service = FoodScanService(db)
    scan = await scan_service.scan_food_image(
        current_user.id,
        data.image_base64,
        data.estimate_portion
    )
    
    return DataResponse(data=scan, message="Food scan completed")


@router.post("/barcode", response_model=DataResponse[FoodScanResponse])
async def scan_barcode(
    data: FoodScanFromBarcode,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Look up food by barcode
    """
    scan_service = FoodScanService(db)
    scan = await scan_service.scan_barcode(current_user.id, data.barcode)
    
    return DataResponse(data=scan)


@router.get("/{scan_id}", response_model=DataResponse[FoodScanResponse])
async def get_scan(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific scan
    """
    scan_service = FoodScanService(db)
    scan = scan_service.get_scan(scan_id, current_user.id)
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    return DataResponse(data=scan)


@router.get("/history", response_model=ListResponse[FoodScanResponse])
async def get_scan_history(
    limit: int = Query(default=20, le=50),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's scan history
    """
    scan_service = FoodScanService(db)
    scans = scan_service.get_user_scans(current_user.id, limit, offset)
    
    return ListResponse(data=scans, total=len(scans))


@router.post("/confirm", response_model=DataResponse[NutritionLogResponse])
async def confirm_scan_result(
    data: ScanResultConfirm,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm scan result and add to nutrition log
    """
    scan_service = FoodScanService(db)
    
    meal_type = MealType(data.meal_type)
    
    log = scan_service.confirm_scan_result(
        current_user.id,
        data.result_id,
        meal_type,
        data.quantity,
        data.serving_size,
        data.notes
    )
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan result not found"
        )
    
    return DataResponse(data=log, message="Added to nutrition log")
