"""
Insights Service
Analytics, trends, and recommendations
"""
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.nutrition import NutritionLog, DailyNutritionSummary
from app.models.exercise import ExerciseLog
from app.models.water import WaterLog
from app.models.walking import StepCount
from app.models.user import UserGoals, UserProfile

logger = get_logger(__name__)


class InsightsService:
    """Analytics and insights service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_data(self, user_id: int, target_date: date = None) -> dict:
        """Get all data needed for dashboard"""
        target_date = target_date or date.today()
        
        goals = self.db.query(UserGoals).filter(UserGoals.user_id == user_id).first()
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        # Today's nutrition
        nutrition_logs = self.db.query(NutritionLog).filter(
            NutritionLog.user_id == user_id,
            NutritionLog.log_date == target_date
        ).all()
        
        calories_consumed = sum(log.calories for log in nutrition_logs)
        protein_consumed = sum(log.protein_g for log in nutrition_logs)
        carbs_consumed = sum(log.carbohydrates_g for log in nutrition_logs)
        fat_consumed = sum(log.fat_g for log in nutrition_logs)
        
        # Today's water
        water_logs = self.db.query(WaterLog).filter(
            WaterLog.user_id == user_id,
            WaterLog.log_date == target_date
        ).all()
        water_consumed = sum(log.amount_ml for log in water_logs)
        
        # Today's exercise
        exercise_logs = self.db.query(ExerciseLog).filter(
            ExerciseLog.user_id == user_id,
            ExerciseLog.log_date == target_date
        ).all()
        calories_burned = sum(log.calories_burned for log in exercise_logs)
        exercise_minutes = sum(log.duration_minutes for log in exercise_logs)
        
        # Today's steps
        step_count = self.db.query(StepCount).filter(
            StepCount.user_id == user_id,
            StepCount.count_date == target_date
        ).first()
        steps_today = step_count.total_steps if step_count else 0
        
        # Goals - use defaults if None
        calorie_goal = (goals.daily_calorie_goal if goals and goals.daily_calorie_goal else None) or 2000
        protein_goal = (goals.protein_goal_g if goals and goals.protein_goal_g else None) or 50
        carbs_goal = (goals.carbs_goal_g if goals and goals.carbs_goal_g else None) or 250
        fat_goal = (goals.fat_goal_g if goals and goals.fat_goal_g else None) or 65
        water_goal = (goals.water_goal_ml if goals and goals.water_goal_ml else None) or 2000
        steps_goal = (goals.daily_steps_goal if goals and goals.daily_steps_goal else None) or 10000
        
        return {
            "date": target_date.isoformat(),
            "nutrition": {
                "calories": {
                    "consumed": calories_consumed,
                    "goal": calorie_goal,
                    "remaining": max(0, calorie_goal - calories_consumed),
                    "percent": round(calories_consumed / calorie_goal * 100, 1) if calorie_goal else 0
                },
                "protein": {
                    "consumed": protein_consumed,
                    "goal": protein_goal,
                    "percent": round(protein_consumed / protein_goal * 100, 1) if protein_goal else 0
                },
                "carbs": {
                    "consumed": carbs_consumed,
                    "goal": carbs_goal,
                    "percent": round(carbs_consumed / carbs_goal * 100, 1) if carbs_goal else 0
                },
                "fat": {
                    "consumed": fat_consumed,
                    "goal": fat_goal,
                    "percent": round(fat_consumed / fat_goal * 100, 1) if fat_goal else 0
                },
                "meals_logged": len(nutrition_logs)
            },
            "water": {
                "consumed": water_consumed,
                "goal": water_goal,
                "remaining": max(0, water_goal - water_consumed),
                "percent": round(water_consumed / water_goal * 100, 1) if water_goal else 0,
                "entries": len(water_logs)
            },
            "exercise": {
                "calories_burned": calories_burned,
                "minutes": exercise_minutes,
                "workouts": len(exercise_logs)
            },
            "steps": {
                "count": steps_today,
                "goal": steps_goal,
                "percent": round(steps_today / steps_goal * 100, 1) if steps_goal else 0
            },
            "net_calories": calories_consumed - calories_burned
        }
    
    def get_weekly_trends(self, user_id: int, end_date: date = None) -> dict:
        """Get weekly trend data for charts"""
        end_date = end_date or date.today()
        start_date = end_date - timedelta(days=6)
        
        days = []
        calories_data = []
        protein_data = []
        carbs_data = []
        fat_data = []
        water_data = []
        steps_data = []
        exercise_data = []
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            days.append(current_date.strftime("%a"))
            
            # Nutrition
            nutrition_logs = self.db.query(NutritionLog).filter(
                NutritionLog.user_id == user_id,
                NutritionLog.log_date == current_date
            ).all()
            
            calories_data.append(sum(log.calories for log in nutrition_logs))
            protein_data.append(sum(log.protein_g for log in nutrition_logs))
            carbs_data.append(sum(log.carbohydrates_g for log in nutrition_logs))
            fat_data.append(sum(log.fat_g for log in nutrition_logs))
            
            # Water
            water_logs = self.db.query(WaterLog).filter(
                WaterLog.user_id == user_id,
                WaterLog.log_date == current_date
            ).all()
            water_data.append(sum(log.amount_ml for log in water_logs))
            
            # Steps
            step_count = self.db.query(StepCount).filter(
                StepCount.user_id == user_id,
                StepCount.count_date == current_date
            ).first()
            steps_data.append(step_count.total_steps if step_count else 0)
            
            # Exercise
            exercise_logs = self.db.query(ExerciseLog).filter(
                ExerciseLog.user_id == user_id,
                ExerciseLog.log_date == current_date
            ).all()
            exercise_data.append(sum(log.calories_burned for log in exercise_logs))
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "labels": days,
            "nutrition": {
                "calories": calories_data,
                "protein": protein_data,
                "carbs": carbs_data,
                "fat": fat_data
            },
            "water": water_data,
            "steps": steps_data,
            "exercise_calories": exercise_data,
            "averages": {
                "calories": round(sum(calories_data) / 7, 0),
                "protein": round(sum(protein_data) / 7, 1),
                "water": round(sum(water_data) / 7, 0),
                "steps": round(sum(steps_data) / 7, 0)
            }
        }
    
    def get_monthly_summary(self, user_id: int, year: int, month: int) -> dict:
        """Get monthly summary statistics"""
        from calendar import monthrange
        
        _, days_in_month = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, days_in_month)
        
        # Aggregate nutrition data
        nutrition_summary = self.db.query(
            func.sum(NutritionLog.calories).label('total_calories'),
            func.avg(NutritionLog.calories).label('avg_calories'),
            func.sum(NutritionLog.protein_g).label('total_protein'),
            func.sum(NutritionLog.carbohydrates_g).label('total_carbs'),
            func.sum(NutritionLog.fat_g).label('total_fat'),
            func.count(func.distinct(NutritionLog.log_date)).label('days_logged')
        ).filter(
            NutritionLog.user_id == user_id,
            NutritionLog.log_date >= start_date,
            NutritionLog.log_date <= end_date
        ).first()
        
        # Aggregate water data
        water_summary = self.db.query(
            func.sum(WaterLog.amount_ml).label('total_water'),
            func.avg(WaterLog.amount_ml).label('avg_water')
        ).filter(
            WaterLog.user_id == user_id,
            WaterLog.log_date >= start_date,
            WaterLog.log_date <= end_date
        ).first()
        
        # Aggregate exercise data
        exercise_summary = self.db.query(
            func.sum(ExerciseLog.calories_burned).label('total_burned'),
            func.sum(ExerciseLog.duration_minutes).label('total_minutes'),
            func.count(ExerciseLog.id).label('workout_count')
        ).filter(
            ExerciseLog.user_id == user_id,
            ExerciseLog.log_date >= start_date,
            ExerciseLog.log_date <= end_date
        ).first()
        
        # Aggregate steps data
        steps_summary = self.db.query(
            func.sum(StepCount.total_steps).label('total_steps'),
            func.avg(StepCount.total_steps).label('avg_steps'),
            func.count(StepCount.id).filter(StepCount.goal_achieved == True).label('days_goal_met')
        ).filter(
            StepCount.user_id == user_id,
            StepCount.count_date >= start_date,
            StepCount.count_date <= end_date
        ).first()
        
        return {
            "period": {
                "year": year,
                "month": month,
                "days_in_month": days_in_month
            },
            "nutrition": {
                "total_calories": nutrition_summary.total_calories or 0,
                "avg_daily_calories": round(nutrition_summary.avg_calories or 0, 0),
                "total_protein_g": nutrition_summary.total_protein or 0,
                "total_carbs_g": nutrition_summary.total_carbs or 0,
                "total_fat_g": nutrition_summary.total_fat or 0,
                "days_logged": nutrition_summary.days_logged or 0
            },
            "water": {
                "total_ml": water_summary.total_water or 0,
                "avg_daily_ml": round(water_summary.avg_water or 0, 0)
            },
            "exercise": {
                "total_calories_burned": exercise_summary.total_burned or 0,
                "total_minutes": exercise_summary.total_minutes or 0,
                "workout_count": exercise_summary.workout_count or 0
            },
            "steps": {
                "total_steps": steps_summary.total_steps or 0,
                "avg_daily_steps": round(steps_summary.avg_steps or 0, 0),
                "days_goal_met": steps_summary.days_goal_met or 0
            }
        }
    
    def get_macro_distribution(self, user_id: int, target_date: date = None) -> dict:
        """Get macronutrient distribution for pie chart"""
        target_date = target_date or date.today()
        
        logs = self.db.query(NutritionLog).filter(
            NutritionLog.user_id == user_id,
            NutritionLog.log_date == target_date
        ).all()
        
        protein_g = sum(log.protein_g for log in logs)
        carbs_g = sum(log.carbohydrates_g for log in logs)
        fat_g = sum(log.fat_g for log in logs)
        
        protein_cal = protein_g * 4
        carbs_cal = carbs_g * 4
        fat_cal = fat_g * 9
        total_cal = protein_cal + carbs_cal + fat_cal
        
        return {
            "date": target_date.isoformat(),
            "macros": {
                "protein": {
                    "grams": round(protein_g, 1),
                    "calories": round(protein_cal, 0),
                    "percent": round(protein_cal / total_cal * 100, 1) if total_cal > 0 else 0
                },
                "carbs": {
                    "grams": round(carbs_g, 1),
                    "calories": round(carbs_cal, 0),
                    "percent": round(carbs_cal / total_cal * 100, 1) if total_cal > 0 else 0
                },
                "fat": {
                    "grams": round(fat_g, 1),
                    "calories": round(fat_cal, 0),
                    "percent": round(fat_cal / total_cal * 100, 1) if total_cal > 0 else 0
                }
            },
            "total_calories": round(total_cal, 0)
        }
    
    def get_recommendations(self, user_id: int) -> List[dict]:
        """Generate personalized recommendations based on user data"""
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        goals = self.db.query(UserGoals).filter(UserGoals.user_id == user_id).first()
        recommendations = []
        
        # Analyze recent nutrition
        nutrition_logs = self.db.query(NutritionLog).filter(
            NutritionLog.user_id == user_id,
            NutritionLog.log_date >= week_ago
        ).all()
        
        if nutrition_logs:
            avg_calories = sum(log.calories for log in nutrition_logs) / 7
            avg_protein = sum(log.protein_g for log in nutrition_logs) / 7
            
            if goals:
                if avg_calories < goals.daily_calorie_goal * 0.8:
                    recommendations.append({
                        "type": "nutrition",
                        "priority": "medium",
                        "title": "Calorie Intake Low",
                        "message": f"Your average calorie intake ({int(avg_calories)}) is below your goal. Consider adding nutrient-dense foods.",
                        "action": "log_food"
                    })
                
                if avg_protein < goals.protein_goal_g * 0.7:
                    recommendations.append({
                        "type": "nutrition",
                        "priority": "medium",
                        "title": "Increase Protein",
                        "message": "Your protein intake is lower than recommended. Try adding lean meats, eggs, or legumes.",
                        "action": "log_food"
                    })
        
        # Analyze water intake
        water_logs = self.db.query(WaterLog).filter(
            WaterLog.user_id == user_id,
            WaterLog.log_date >= week_ago
        ).all()
        
        if water_logs:
            avg_water = sum(log.amount_ml for log in water_logs) / 7
            water_goal = goals.water_goal_ml if goals else 2000
            
            if avg_water < water_goal * 0.7:
                recommendations.append({
                    "type": "water",
                    "priority": "high",
                    "title": "Stay Hydrated",
                    "message": "Your water intake has been below target. Try setting reminders throughout the day.",
                    "action": "log_water"
                })
        
        # Analyze exercise
        exercise_logs = self.db.query(ExerciseLog).filter(
            ExerciseLog.user_id == user_id,
            ExerciseLog.log_date >= week_ago
        ).all()
        
        total_exercise_minutes = sum(log.duration_minutes for log in exercise_logs)
        exercise_goal = goals.weekly_exercise_minutes if goals else 150
        
        if total_exercise_minutes < exercise_goal * 0.5:
            recommendations.append({
                "type": "exercise",
                "priority": "medium",
                "title": "Get Moving!",
                "message": f"You've logged {total_exercise_minutes} minutes this week. Try to fit in more activity!",
                "action": "log_exercise"
            })
        
        # Analyze steps
        step_counts = self.db.query(StepCount).filter(
            StepCount.user_id == user_id,
            StepCount.count_date >= week_ago
        ).all()
        
        if step_counts:
            avg_steps = sum(sc.total_steps for sc in step_counts) / 7
            steps_goal = goals.daily_steps_goal if goals else 10000
            
            if avg_steps < steps_goal * 0.6:
                recommendations.append({
                    "type": "walking",
                    "priority": "low",
                    "title": "Take More Steps",
                    "message": f"Your average is {int(avg_steps)} steps. Try parking farther or taking short walks.",
                    "action": "log_walking"
                })
        
        return recommendations
