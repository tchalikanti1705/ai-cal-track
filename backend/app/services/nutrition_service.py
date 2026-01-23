"""
Nutrition Service
Handles food entries, nutrition logging, and daily summaries
"""
from datetime import date, datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.nutrition import FoodEntry, NutritionLog, DailyNutritionSummary, MealType, FoodSource
from app.models.user import UserGoals
from app.schemas.nutrition import (
    FoodEntryCreate, FoodEntryUpdate,
    NutritionLogCreate, NutritionLogUpdate,
    DailySummaryResponse, MealSummary, WeeklySummaryResponse, MacroBreakdown
)

logger = get_logger(__name__)


class NutritionService:
    """Nutrition tracking service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============ Food Entry Management ============
    
    def search_foods(
        self, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[FoodEntry]:
        """Search food database"""
        search = f"%{query}%"
        
        q = self.db.query(FoodEntry).filter(
            FoodEntry.name.ilike(search)
        )
        
        if category:
            q = q.filter(FoodEntry.category == category)
        
        # Prioritize verified entries
        q = q.order_by(FoodEntry.is_verified.desc(), FoodEntry.name)
        
        return q.limit(limit).all()
    
    def get_food_by_id(self, food_id: int) -> Optional[FoodEntry]:
        """Get food entry by ID"""
        return self.db.query(FoodEntry).filter(FoodEntry.id == food_id).first()
    
    def get_food_by_barcode(self, barcode: str) -> Optional[FoodEntry]:
        """Get food entry by barcode"""
        return self.db.query(FoodEntry).filter(FoodEntry.barcode == barcode).first()
    
    def create_food_entry(self, data: FoodEntryCreate) -> FoodEntry:
        """Create new food entry"""
        food = FoodEntry(**data.model_dump())
        
        self.db.add(food)
        self.db.commit()
        self.db.refresh(food)
        
        logger.info(f"Food entry created: {food.name} (ID: {food.id})")
        return food
    
    def update_food_entry(
        self, 
        food_id: int, 
        data: FoodEntryUpdate
    ) -> Optional[FoodEntry]:
        """Update food entry"""
        food = self.get_food_by_id(food_id)
        
        if not food:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(food, field, value)
        
        self.db.commit()
        self.db.refresh(food)
        
        return food
    
    # ============ Nutrition Logging ============
    
    def log_food(self, user_id: int, data: NutritionLogCreate) -> NutritionLog:
        """Log food consumption"""
        log = NutritionLog(
            user_id=user_id,
            **data.model_dump()
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        # Update daily summary
        self._update_daily_summary(user_id, data.log_date)
        
        logger.info(f"Food logged for user {user_id}: {data.food_name}")
        return log
    
    def quick_add_calories(
        self,
        user_id: int,
        log_date: date,
        meal_type: MealType,
        calories: float,
        name: str = "Quick Add"
    ) -> NutritionLog:
        """Quick add calories without full food details"""
        log = NutritionLog(
            user_id=user_id,
            log_date=log_date,
            meal_type=meal_type,
            food_name=name,
            quantity=1,
            serving_size=1,
            serving_unit="serving",
            calories=calories,
            protein_g=0,
            carbohydrates_g=0,
            fat_g=0,
            fiber_g=0,
            sugar_g=0,
            source=FoodSource.QUICK_ADD
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        self._update_daily_summary(user_id, log_date)
        
        return log
    
    def get_nutrition_log(self, log_id: int, user_id: int) -> Optional[NutritionLog]:
        """Get specific nutrition log"""
        return self.db.query(NutritionLog).filter(
            NutritionLog.id == log_id,
            NutritionLog.user_id == user_id
        ).first()
    
    def update_nutrition_log(
        self,
        log_id: int,
        user_id: int,
        data: NutritionLogUpdate
    ) -> Optional[NutritionLog]:
        """Update nutrition log"""
        log = self.get_nutrition_log(log_id, user_id)
        
        if not log:
            return None
        
        log_date = log.log_date
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(log, field, value)
        
        self.db.commit()
        self.db.refresh(log)
        
        self._update_daily_summary(user_id, log_date)
        
        return log
    
    def delete_nutrition_log(self, log_id: int, user_id: int) -> bool:
        """Delete nutrition log"""
        log = self.get_nutrition_log(log_id, user_id)
        
        if not log:
            return False
        
        log_date = log.log_date
        
        self.db.delete(log)
        self.db.commit()
        
        self._update_daily_summary(user_id, log_date)
        
        logger.info(f"Nutrition log deleted: {log_id}")
        return True
    
    def get_logs_by_date(
        self,
        user_id: int,
        log_date: date
    ) -> List[NutritionLog]:
        """Get all nutrition logs for a specific date"""
        return self.db.query(NutritionLog).filter(
            NutritionLog.user_id == user_id,
            NutritionLog.log_date == log_date
        ).order_by(NutritionLog.log_time).all()
    
    def get_logs_by_meal(
        self,
        user_id: int,
        log_date: date,
        meal_type: MealType
    ) -> List[NutritionLog]:
        """Get nutrition logs for specific meal"""
        return self.db.query(NutritionLog).filter(
            NutritionLog.user_id == user_id,
            NutritionLog.log_date == log_date,
            NutritionLog.meal_type == meal_type
        ).order_by(NutritionLog.log_time).all()
    
    # ============ Daily Summary ============
    
    def get_daily_summary(self, user_id: int, summary_date: date) -> DailySummaryResponse:
        """Get daily nutrition summary with meal breakdown"""
        logs = self.get_logs_by_date(user_id, summary_date)
        goals = self.db.query(UserGoals).filter(UserGoals.user_id == user_id).first()
        
        # Calculate totals
        total_calories = sum(log.calories for log in logs)
        total_protein = sum(log.protein_g for log in logs)
        total_carbs = sum(log.carbohydrates_g for log in logs)
        total_fat = sum(log.fat_g for log in logs)
        total_fiber = sum(log.fiber_g for log in logs)
        total_sugar = sum(log.sugar_g for log in logs)
        total_sodium = sum(log.sodium_mg or 0 for log in logs)
        
        # Get goals
        calorie_goal = goals.daily_calorie_goal if goals else None
        protein_goal = goals.protein_goal_g if goals else None
        carbs_goal = goals.carbs_goal_g if goals else None
        fat_goal = goals.fat_goal_g if goals else None
        
        # Build meal summaries
        meals = []
        for meal_type in MealType:
            meal_logs = [l for l in logs if l.meal_type == meal_type]
            if meal_logs:
                meal_summary = MealSummary(
                    meal_type=meal_type,
                    total_calories=sum(l.calories for l in meal_logs),
                    total_protein_g=sum(l.protein_g for l in meal_logs),
                    total_carbs_g=sum(l.carbohydrates_g for l in meal_logs),
                    total_fat_g=sum(l.fat_g for l in meal_logs),
                    items_count=len(meal_logs),
                    items=meal_logs
                )
                meals.append(meal_summary)
        
        return DailySummaryResponse(
            date=summary_date,
            total_calories=total_calories,
            calorie_goal=calorie_goal,
            calories_remaining=(calorie_goal - total_calories) if calorie_goal else 0,
            calorie_goal_percent=(total_calories / calorie_goal * 100) if calorie_goal else 0,
            total_protein_g=total_protein,
            protein_goal_g=protein_goal,
            protein_goal_percent=(total_protein / protein_goal * 100) if protein_goal else 0,
            total_carbs_g=total_carbs,
            carbs_goal_g=carbs_goal,
            carbs_goal_percent=(total_carbs / carbs_goal * 100) if carbs_goal else 0,
            total_fat_g=total_fat,
            fat_goal_g=fat_goal,
            fat_goal_percent=(total_fat / fat_goal * 100) if fat_goal else 0,
            total_fiber_g=total_fiber,
            total_sugar_g=total_sugar,
            total_sodium_mg=total_sodium,
            meals=meals,
            total_items=len(logs)
        )
    
    def get_weekly_summary(
        self,
        user_id: int,
        start_date: date
    ) -> WeeklySummaryResponse:
        """Get weekly nutrition summary"""
        end_date = start_date + timedelta(days=6)
        
        daily_summaries = []
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        days_logged = 0
        days_on_goal = 0
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            summary = self.get_daily_summary(user_id, current_date)
            daily_summaries.append(summary)
            
            if summary.total_items > 0:
                days_logged += 1
                total_calories += summary.total_calories
                total_protein += summary.total_protein_g
                total_carbs += summary.total_carbs_g
                total_fat += summary.total_fat_g
                
                if summary.calorie_goal and summary.total_calories <= summary.calorie_goal * 1.1:
                    days_on_goal += 1
        
        return WeeklySummaryResponse(
            start_date=start_date,
            end_date=end_date,
            daily_summaries=daily_summaries,
            avg_calories=total_calories / days_logged if days_logged > 0 else 0,
            avg_protein_g=total_protein / days_logged if days_logged > 0 else 0,
            avg_carbs_g=total_carbs / days_logged if days_logged > 0 else 0,
            avg_fat_g=total_fat / days_logged if days_logged > 0 else 0,
            total_calories=total_calories,
            days_logged=days_logged,
            days_on_goal=days_on_goal
        )
    
    def get_macro_breakdown(self, user_id: int, log_date: date) -> MacroBreakdown:
        """Get macronutrient breakdown for a day"""
        logs = self.get_logs_by_date(user_id, log_date)
        
        protein_g = sum(log.protein_g for log in logs)
        carbs_g = sum(log.carbohydrates_g for log in logs)
        fat_g = sum(log.fat_g for log in logs)
        
        protein_calories = protein_g * 4
        carbs_calories = carbs_g * 4
        fat_calories = fat_g * 9
        
        total_calories = protein_calories + carbs_calories + fat_calories
        
        return MacroBreakdown(
            protein_g=protein_g,
            protein_calories=protein_calories,
            protein_percent=(protein_calories / total_calories * 100) if total_calories > 0 else 0,
            carbs_g=carbs_g,
            carbs_calories=carbs_calories,
            carbs_percent=(carbs_calories / total_calories * 100) if total_calories > 0 else 0,
            fat_g=fat_g,
            fat_calories=fat_calories,
            fat_percent=(fat_calories / total_calories * 100) if total_calories > 0 else 0,
            total_calories=total_calories
        )
    
    def _update_daily_summary(self, user_id: int, summary_date: date):
        """Update or create daily summary cache"""
        logs = self.get_logs_by_date(user_id, summary_date)
        goals = self.db.query(UserGoals).filter(UserGoals.user_id == user_id).first()
        
        summary = self.db.query(DailyNutritionSummary).filter(
            DailyNutritionSummary.user_id == user_id,
            DailyNutritionSummary.summary_date == summary_date
        ).first()
        
        if not summary:
            summary = DailyNutritionSummary(
                user_id=user_id,
                summary_date=summary_date
            )
            self.db.add(summary)
        
        # Calculate totals
        summary.total_calories = sum(log.calories for log in logs)
        summary.total_protein_g = sum(log.protein_g for log in logs)
        summary.total_carbs_g = sum(log.carbohydrates_g for log in logs)
        summary.total_fat_g = sum(log.fat_g for log in logs)
        summary.total_fiber_g = sum(log.fiber_g for log in logs)
        summary.total_sugar_g = sum(log.sugar_g for log in logs)
        summary.total_sodium_mg = sum(log.sodium_mg or 0 for log in logs)
        
        # Meal breakdown
        breakfast_logs = [l for l in logs if l.meal_type == MealType.BREAKFAST]
        lunch_logs = [l for l in logs if l.meal_type == MealType.LUNCH]
        dinner_logs = [l for l in logs if l.meal_type == MealType.DINNER]
        snack_types = [MealType.MORNING_SNACK, MealType.AFTERNOON_SNACK, MealType.EVENING_SNACK]
        snack_logs = [l for l in logs if l.meal_type in snack_types]
        
        summary.breakfast_calories = sum(l.calories for l in breakfast_logs)
        summary.lunch_calories = sum(l.calories for l in lunch_logs)
        summary.dinner_calories = sum(l.calories for l in dinner_logs)
        summary.snacks_calories = sum(l.calories for l in snack_logs)
        
        # Goal percentages
        if goals:
            if goals.daily_calorie_goal:
                summary.calorie_goal_percent = summary.total_calories / goals.daily_calorie_goal * 100
            if goals.protein_goal_g:
                summary.protein_goal_percent = summary.total_protein_g / goals.protein_goal_g * 100
            if goals.carbs_goal_g:
                summary.carbs_goal_percent = summary.total_carbs_g / goals.carbs_goal_g * 100
            if goals.fat_goal_g:
                summary.fat_goal_percent = summary.total_fat_g / goals.fat_goal_g * 100
        
        summary.meals_logged = len(set(l.meal_type for l in logs))
        summary.foods_logged = len(logs)
        
        self.db.commit()
