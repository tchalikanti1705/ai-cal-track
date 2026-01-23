"""
User Service
Handles user profile and goals management
"""
from datetime import date
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.user import User, UserProfile, UserGoals, OnboardingResponse, GoalType
from app.schemas.user import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    UserGoalsCreate, UserGoalsUpdate, UserGoalsResponse,
    OnboardingSubmit
)

logger = get_logger(__name__)

# Onboarding questions configuration
ONBOARDING_QUESTIONS = [
    {
        "step": 1,
        "key": "primary_goal",
        "text": "What's your primary health goal?",
        "type": "single_choice",
        "options": [
            {"value": "lose_weight", "label": "Lose Weight"},
            {"value": "gain_weight", "label": "Gain Weight"},
            {"value": "maintain_weight", "label": "Maintain Weight"},
            {"value": "build_muscle", "label": "Build Muscle"},
            {"value": "improve_health", "label": "Improve Overall Health"}
        ]
    },
    {
        "step": 2,
        "key": "activity_level",
        "text": "How active are you on a typical day?",
        "type": "single_choice",
        "options": [
            {"value": "sedentary", "label": "Sedentary (desk job, little exercise)"},
            {"value": "lightly_active", "label": "Lightly Active (1-2 workouts/week)"},
            {"value": "moderately_active", "label": "Moderately Active (3-5 workouts/week)"},
            {"value": "very_active", "label": "Very Active (6-7 workouts/week)"},
            {"value": "extra_active", "label": "Extra Active (physical job + exercise)"}
        ]
    },
    {
        "step": 3,
        "key": "personal_info",
        "text": "Tell us about yourself",
        "type": "form",
        "fields": ["gender", "date_of_birth", "height_cm", "current_weight_kg"]
    },
    {
        "step": 4,
        "key": "target_weight",
        "text": "What's your target weight?",
        "type": "number",
        "unit": "kg"
    },
    {
        "step": 5,
        "key": "dietary_preference",
        "text": "Do you follow any specific diet?",
        "type": "single_choice",
        "options": [
            {"value": "none", "label": "No specific diet"},
            {"value": "vegetarian", "label": "Vegetarian"},
            {"value": "vegan", "label": "Vegan"},
            {"value": "keto", "label": "Keto"},
            {"value": "paleo", "label": "Paleo"},
            {"value": "gluten_free", "label": "Gluten-free"}
        ]
    },
    {
        "step": 6,
        "key": "tracking_preferences",
        "text": "What would you like to track?",
        "type": "multiple_choice",
        "options": [
            {"value": "calories", "label": "Calories"},
            {"value": "macros", "label": "Macronutrients"},
            {"value": "water", "label": "Water Intake"},
            {"value": "exercise", "label": "Exercise"},
            {"value": "steps", "label": "Daily Steps"}
        ]
    }
]


class UserService:
    """User profile and goals management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    # ============ Profile Management ============
    
    def get_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile"""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    def create_profile(self, user_id: int, data: UserProfileCreate) -> UserProfile:
        """Create user profile"""
        profile = UserProfile(
            user_id=user_id,
            **data.model_dump(exclude_unset=True)
        )
        
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        
        logger.info(f"Profile created for user: {user_id}")
        return profile
    
    def update_profile(self, user_id: int, data: UserProfileUpdate) -> Optional[UserProfile]:
        """Update user profile"""
        profile = self.get_profile(user_id)
        
        if not profile:
            logger.warning(f"Profile not found for user: {user_id}")
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        self.db.commit()
        self.db.refresh(profile)
        
        logger.info(f"Profile updated for user: {user_id}")
        return profile
    
    def get_profile_with_calculations(self, user_id: int) -> Optional[dict]:
        """Get profile with calculated values (BMI, BMR, TDEE)"""
        profile = self.get_profile(user_id)
        
        if not profile:
            return None
        
        profile_dict = {
            "id": profile.id,
            "user_id": profile.user_id,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "date_of_birth": profile.date_of_birth,
            "gender": profile.gender,
            "height_cm": profile.height_cm,
            "current_weight_kg": profile.current_weight_kg,
            "target_weight_kg": profile.target_weight_kg,
            "activity_level": profile.activity_level,
            "dietary_preference": profile.dietary_preference,
            "allergies": profile.allergies or [],
            "health_conditions": profile.health_conditions or [],
            "timezone": profile.timezone,
            "measurement_system": profile.measurement_system,
            "profile_image_url": profile.profile_image_url,
            "onboarding_completed": profile.onboarding_completed,
            "onboarding_step": profile.onboarding_step,
            "age": profile.age,
            "bmi": profile.bmi,
            "bmr": profile.calculate_bmr(),
            "tdee": profile.calculate_tdee()
        }
        
        return profile_dict
    
    # ============ Goals Management ============
    
    def get_goals(self, user_id: int) -> Optional[UserGoals]:
        """Get user goals"""
        return self.db.query(UserGoals).filter(UserGoals.user_id == user_id).first()
    
    def create_goals(self, user_id: int, data: UserGoalsCreate) -> UserGoals:
        """Create user goals"""
        goals = UserGoals(
            user_id=user_id,
            **data.model_dump(exclude_unset=True)
        )
        
        self.db.add(goals)
        self.db.commit()
        self.db.refresh(goals)
        
        logger.info(f"Goals created for user: {user_id}")
        return goals
    
    def update_goals(self, user_id: int, data: UserGoalsUpdate) -> Optional[UserGoals]:
        """Update user goals"""
        goals = self.get_goals(user_id)
        
        if not goals:
            logger.warning(f"Goals not found for user: {user_id}")
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(goals, field, value)
        
        self.db.commit()
        self.db.refresh(goals)
        
        logger.info(f"Goals updated for user: {user_id}")
        return goals
    
    def calculate_recommended_goals(self, user_id: int) -> dict:
        """Calculate recommended nutrition goals based on profile"""
        profile = self.get_profile(user_id)
        goals = self.get_goals(user_id)
        
        if not profile:
            return {}
        
        tdee = profile.calculate_tdee()
        
        # Adjust calories based on goal
        if goals:
            if goals.goal_type == GoalType.LOSE_WEIGHT:
                calorie_goal = tdee - 500  # ~0.5kg/week loss
            elif goals.goal_type == GoalType.GAIN_WEIGHT:
                calorie_goal = tdee + 300  # Lean gain
            else:
                calorie_goal = tdee
        else:
            calorie_goal = tdee
        
        calorie_goal = max(1200, int(calorie_goal))  # Minimum 1200 calories
        
        # Calculate macros (moderate split)
        # 30% protein, 40% carbs, 30% fat
        protein_g = int((calorie_goal * 0.30) / 4)
        carbs_g = int((calorie_goal * 0.40) / 4)
        fat_g = int((calorie_goal * 0.30) / 9)
        
        return {
            "daily_calorie_goal": calorie_goal,
            "protein_goal_g": protein_g,
            "carbs_goal_g": carbs_g,
            "fat_goal_g": fat_g,
            "tdee": tdee,
            "bmr": profile.calculate_bmr()
        }
    
    # ============ Onboarding ============
    
    def get_onboarding_questions(self) -> List[dict]:
        """Get all onboarding questions"""
        return ONBOARDING_QUESTIONS
    
    def get_onboarding_progress(self, user_id: int) -> dict:
        """Get user's onboarding progress"""
        profile = self.get_profile(user_id)
        
        if not profile:
            return {
                "current_step": 0,
                "total_steps": len(ONBOARDING_QUESTIONS),
                "completed": False,
                "responses": []
            }
        
        responses = self.db.query(OnboardingResponse).filter(
            OnboardingResponse.user_id == user_id
        ).all()
        
        return {
            "current_step": profile.onboarding_step,
            "total_steps": len(ONBOARDING_QUESTIONS),
            "completed": profile.onboarding_completed,
            "responses": [
                {
                    "question_key": r.question_key,
                    "response_value": r.response_value,
                    "step_number": r.step_number
                }
                for r in responses
            ]
        }
    
    def submit_onboarding_response(
        self, 
        user_id: int, 
        data: OnboardingSubmit
    ) -> Tuple[bool, str]:
        """Submit onboarding responses"""
        profile = self.get_profile(user_id)
        
        if not profile:
            return False, "Profile not found"
        
        try:
            for response in data.responses:
                # Check if response already exists
                existing = self.db.query(OnboardingResponse).filter(
                    OnboardingResponse.user_id == user_id,
                    OnboardingResponse.question_key == response.question_key
                ).first()
                
                if existing:
                    existing.response_value = response.response_value
                    existing.response_metadata = response.response_metadata
                else:
                    question = next(
                        (q for q in ONBOARDING_QUESTIONS if q["key"] == response.question_key),
                        None
                    )
                    
                    onboarding_response = OnboardingResponse(
                        user_id=user_id,
                        question_key=response.question_key,
                        question_text=question["text"] if question else "",
                        response_value=response.response_value,
                        response_metadata=response.response_metadata,
                        step_number=data.step_number
                    )
                    self.db.add(onboarding_response)
            
            # Update profile step
            profile.onboarding_step = data.step_number
            
            # Check if onboarding is complete
            if data.step_number >= len(ONBOARDING_QUESTIONS):
                profile.onboarding_completed = True
                self._apply_onboarding_to_profile(user_id)
            
            self.db.commit()
            
            logger.info(f"Onboarding step {data.step_number} completed for user: {user_id}")
            return True, "Response saved"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Onboarding error: {e}", exc_info=True)
            return False, "Failed to save response"
    
    def _apply_onboarding_to_profile(self, user_id: int):
        """Apply onboarding responses to user profile and goals"""
        responses = self.db.query(OnboardingResponse).filter(
            OnboardingResponse.user_id == user_id
        ).all()
        
        profile = self.get_profile(user_id)
        goals = self.get_goals(user_id)
        
        response_map = {r.question_key: r.response_value for r in responses}
        
        # Apply to profile
        if "activity_level" in response_map:
            from app.models.user import ActivityLevel
            try:
                profile.activity_level = ActivityLevel(response_map["activity_level"])
            except ValueError:
                pass
        
        if "dietary_preference" in response_map:
            from app.models.user import DietaryPreference
            try:
                profile.dietary_preference = DietaryPreference(response_map["dietary_preference"])
            except ValueError:
                pass
        
        # Apply to goals
        if goals and "primary_goal" in response_map:
            try:
                goals.goal_type = GoalType(response_map["primary_goal"])
            except ValueError:
                pass
        
        # Calculate and set calorie goals
        recommended = self.calculate_recommended_goals(user_id)
        if goals and recommended:
            goals.daily_calorie_goal = recommended.get("daily_calorie_goal")
            goals.protein_goal_g = recommended.get("protein_goal_g")
            goals.carbs_goal_g = recommended.get("carbs_goal_g")
            goals.fat_goal_g = recommended.get("fat_goal_g")
        
        self.db.commit()
        logger.info(f"Onboarding applied to profile for user: {user_id}")
