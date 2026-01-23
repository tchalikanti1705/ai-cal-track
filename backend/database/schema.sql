-- AI Food Tracking Database Schema
-- PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- USERS TABLES
-- =====================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
    verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_users_email ON users(email);

CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(20),
    height_cm FLOAT,
    current_weight_kg FLOAT,
    target_weight_kg FLOAT,
    activity_level VARCHAR(30) DEFAULT 'moderately_active',
    dietary_preference VARCHAR(30) DEFAULT 'none',
    allergies JSONB DEFAULT '[]',
    health_conditions JSONB DEFAULT '[]',
    timezone VARCHAR(50) DEFAULT 'UTC',
    measurement_system VARCHAR(10) DEFAULT 'metric',
    profile_image_url VARCHAR(500),
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_step INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE user_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goal_type VARCHAR(30) DEFAULT 'maintain_weight',
    daily_calorie_goal INTEGER,
    is_calorie_goal_custom BOOLEAN DEFAULT FALSE,
    protein_goal_g INTEGER,
    carbs_goal_g INTEGER,
    fat_goal_g INTEGER,
    fiber_goal_g INTEGER DEFAULT 25,
    sodium_limit_mg INTEGER DEFAULT 2300,
    sugar_limit_g INTEGER DEFAULT 50,
    water_goal_ml INTEGER DEFAULT 2000,
    weekly_exercise_minutes INTEGER DEFAULT 150,
    daily_steps_goal INTEGER DEFAULT 10000,
    weekly_workout_days INTEGER DEFAULT 3,
    weight_goal_kg FLOAT,
    weight_change_rate FLOAT DEFAULT 0.5,
    track_calories BOOLEAN DEFAULT TRUE,
    track_macros BOOLEAN DEFAULT TRUE,
    track_water BOOLEAN DEFAULT TRUE,
    track_exercise BOOLEAN DEFAULT TRUE,
    track_steps BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE onboarding_responses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_key VARCHAR(100) NOT NULL,
    question_text TEXT NOT NULL,
    response_value VARCHAR(255) NOT NULL,
    response_metadata JSONB,
    step_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(user_id, question_key)
);

-- =====================================================
-- NUTRITION TABLES
-- =====================================================

CREATE TABLE food_entries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    barcode VARCHAR(50),
    serving_size FLOAT NOT NULL DEFAULT 100,
    serving_unit VARCHAR(50) NOT NULL DEFAULT 'g',
    servings_per_container FLOAT,
    calories FLOAT NOT NULL DEFAULT 0,
    protein_g FLOAT NOT NULL DEFAULT 0,
    carbohydrates_g FLOAT NOT NULL DEFAULT 0,
    fat_g FLOAT NOT NULL DEFAULT 0,
    fiber_g FLOAT NOT NULL DEFAULT 0,
    sugar_g FLOAT NOT NULL DEFAULT 0,
    saturated_fat_g FLOAT,
    trans_fat_g FLOAT,
    cholesterol_mg FLOAT,
    sodium_mg FLOAT,
    potassium_mg FLOAT,
    vitamin_a_percent FLOAT,
    vitamin_c_percent FLOAT,
    vitamin_d_percent FLOAT,
    calcium_percent FLOAT,
    iron_percent FLOAT,
    category VARCHAR(100),
    image_url VARCHAR(500),
    is_verified INTEGER DEFAULT 0,
    source VARCHAR(100),
    external_id VARCHAR(100),
    extended_nutrition JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_food_entries_name ON food_entries(name);
CREATE INDEX idx_food_entries_barcode ON food_entries(barcode);

CREATE TABLE nutrition_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    food_entry_id INTEGER REFERENCES food_entries(id) ON DELETE SET NULL,
    log_date DATE NOT NULL,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meal_type VARCHAR(30) NOT NULL,
    food_name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    quantity FLOAT NOT NULL DEFAULT 1,
    serving_size FLOAT NOT NULL,
    serving_unit VARCHAR(50) NOT NULL,
    calories FLOAT NOT NULL DEFAULT 0,
    protein_g FLOAT NOT NULL DEFAULT 0,
    carbohydrates_g FLOAT NOT NULL DEFAULT 0,
    fat_g FLOAT NOT NULL DEFAULT 0,
    fiber_g FLOAT NOT NULL DEFAULT 0,
    sugar_g FLOAT NOT NULL DEFAULT 0,
    sodium_mg FLOAT,
    source VARCHAR(30) DEFAULT 'manual',
    food_scan_id INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_nutrition_logs_user_date ON nutrition_logs(user_id, log_date);
CREATE INDEX idx_nutrition_logs_user_meal ON nutrition_logs(user_id, log_date, meal_type);

CREATE TABLE daily_nutrition_summaries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    summary_date DATE NOT NULL,
    total_calories FLOAT DEFAULT 0,
    total_protein_g FLOAT DEFAULT 0,
    total_carbs_g FLOAT DEFAULT 0,
    total_fat_g FLOAT DEFAULT 0,
    total_fiber_g FLOAT DEFAULT 0,
    total_sugar_g FLOAT DEFAULT 0,
    total_sodium_mg FLOAT DEFAULT 0,
    breakfast_calories FLOAT DEFAULT 0,
    lunch_calories FLOAT DEFAULT 0,
    dinner_calories FLOAT DEFAULT 0,
    snacks_calories FLOAT DEFAULT 0,
    calorie_goal_percent FLOAT DEFAULT 0,
    protein_goal_percent FLOAT DEFAULT 0,
    carbs_goal_percent FLOAT DEFAULT 0,
    fat_goal_percent FLOAT DEFAULT 0,
    meals_logged INTEGER DEFAULT 0,
    foods_logged INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(user_id, summary_date)
);

-- =====================================================
-- EXERCISE TABLES
-- =====================================================

CREATE TABLE exercise_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(30) NOT NULL,
    description TEXT,
    met_light FLOAT DEFAULT 3.0,
    met_moderate FLOAT DEFAULT 5.0,
    met_vigorous FLOAT DEFAULT 8.0,
    met_maximum FLOAT DEFAULT 10.0,
    default_intensity VARCHAR(20) DEFAULT 'moderate',
    is_cardio BOOLEAN DEFAULT FALSE,
    is_strength BOOLEAN DEFAULT FALSE,
    burns_calories BOOLEAN DEFAULT TRUE,
    icon VARCHAR(100),
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(30) NOT NULL,
    description TEXT,
    instructions TEXT,
    met_value FLOAT DEFAULT 5.0,
    typical_duration_minutes INTEGER DEFAULT 30,
    muscle_groups JSONB DEFAULT '[]',
    equipment JSONB DEFAULT '[]',
    difficulty_level VARCHAR(20) DEFAULT 'intermediate',
    image_url VARCHAR(500),
    video_url VARCHAR(500),
    popularity_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_exercises_category ON exercises(category);

CREATE TABLE exercise_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_type_id INTEGER REFERENCES exercise_types(id),
    log_date DATE NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_minutes INTEGER NOT NULL,
    exercise_name VARCHAR(255) NOT NULL,
    category VARCHAR(30) NOT NULL,
    intensity VARCHAR(20) DEFAULT 'moderate',
    calories_burned FLOAT NOT NULL DEFAULT 0,
    is_calories_manual BOOLEAN DEFAULT FALSE,
    distance_km FLOAT,
    pace_min_per_km FLOAT,
    avg_heart_rate INTEGER,
    max_heart_rate INTEGER,
    sets INTEGER,
    reps INTEGER,
    weight_kg FLOAT,
    notes TEXT,
    location VARCHAR(255),
    weather VARCHAR(100),
    source VARCHAR(50) DEFAULT 'manual',
    external_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_exercise_logs_user_date ON exercise_logs(user_id, log_date);

-- =====================================================
-- WATER TRACKING TABLES
-- =====================================================

CREATE TABLE water_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    log_date DATE NOT NULL,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount_ml INTEGER NOT NULL,
    container_type VARCHAR(30) DEFAULT 'custom',
    beverage_type VARCHAR(50) DEFAULT 'water',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_water_logs_user_date ON water_logs(user_id, log_date);

CREATE TABLE water_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    daily_goal_ml INTEGER NOT NULL DEFAULT 2000,
    reminder_enabled INTEGER DEFAULT 1,
    reminder_interval_minutes INTEGER DEFAULT 60,
    reminder_start_time VARCHAR(5) DEFAULT '08:00',
    reminder_end_time VARCHAR(5) DEFAULT '22:00',
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_water_goals_user ON water_goals(user_id, effective_from);

-- =====================================================
-- WALKING/STEPS TABLES
-- =====================================================

CREATE TABLE walking_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_date DATE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    steps INTEGER NOT NULL DEFAULT 0,
    distance_meters FLOAT,
    calories_burned FLOAT,
    avg_pace_min_per_km FLOAT,
    avg_speed_kmh FLOAT,
    max_speed_kmh FLOAT,
    elevation_gain_m FLOAT,
    elevation_loss_m FLOAT,
    avg_heart_rate INTEGER,
    max_heart_rate INTEGER,
    route_data JSONB,
    activity_type VARCHAR(50) DEFAULT 'walking',
    title VARCHAR(255),
    notes TEXT,
    weather VARCHAR(100),
    is_outdoor BOOLEAN DEFAULT TRUE,
    source VARCHAR(50) DEFAULT 'manual',
    external_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_walking_sessions_user_date ON walking_sessions(user_id, session_date);

CREATE TABLE step_counts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    count_date DATE NOT NULL,
    total_steps INTEGER NOT NULL DEFAULT 0,
    step_goal INTEGER NOT NULL DEFAULT 10000,
    goal_achieved BOOLEAN DEFAULT FALSE,
    total_distance_meters FLOAT,
    total_calories_burned FLOAT,
    active_minutes INTEGER DEFAULT 0,
    walking_minutes INTEGER DEFAULT 0,
    running_minutes INTEGER DEFAULT 0,
    hourly_steps JSONB,
    data_source VARCHAR(50) DEFAULT 'calculated',
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(user_id, count_date)
);

-- =====================================================
-- FOOD SCANNING TABLES
-- =====================================================

CREATE TABLE food_scans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scan_type VARCHAR(20) DEFAULT 'photo',
    status VARCHAR(20) DEFAULT 'pending',
    image_url VARCHAR(500),
    image_base64 TEXT,
    barcode VARCHAR(50),
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    processing_time_ms INTEGER,
    model_used VARCHAR(100),
    model_version VARCHAR(50),
    confidence_score FLOAT,
    raw_response JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    user_confirmed BOOLEAN,
    user_corrected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_food_scans_user_date ON food_scans(user_id, scanned_at);
CREATE INDEX idx_food_scans_status ON food_scans(status);

CREATE TABLE food_scan_results (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER NOT NULL REFERENCES food_scans(id) ON DELETE CASCADE,
    food_name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    confidence FLOAT NOT NULL DEFAULT 0,
    bounding_box JSONB,
    estimated_portion VARCHAR(100),
    estimated_weight_g FLOAT,
    estimated_calories FLOAT,
    estimated_protein_g FLOAT,
    estimated_carbs_g FLOAT,
    estimated_fat_g FLOAT,
    nutrition_data JSONB,
    matched_food_entry_id INTEGER REFERENCES food_entries(id),
    match_confidence FLOAT,
    alternative_matches JSONB,
    user_selected_name VARCHAR(255),
    user_adjusted_portion FLOAT,
    added_to_log BOOLEAN DEFAULT FALSE,
    nutrition_log_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_food_scan_results_scan ON food_scan_results(scan_id);

-- =====================================================
-- SEED DATA
-- =====================================================

-- Insert common exercise types
INSERT INTO exercise_types (name, category, description, met_light, met_moderate, met_vigorous, is_cardio, is_strength) VALUES
('Walking', 'walking', 'Walking at various paces', 2.5, 3.5, 5.0, TRUE, FALSE),
('Running', 'running', 'Running at various paces', 6.0, 8.0, 11.0, TRUE, FALSE),
('Cycling', 'cycling', 'Cycling at various intensities', 4.0, 6.0, 10.0, TRUE, FALSE),
('Swimming', 'swimming', 'Swimming laps', 5.0, 7.0, 10.0, TRUE, FALSE),
('Weight Training', 'strength', 'Resistance training with weights', 3.0, 5.0, 6.0, FALSE, TRUE),
('Yoga', 'yoga', 'Various yoga practices', 2.5, 3.0, 4.0, FALSE, FALSE),
('HIIT', 'hiit', 'High-intensity interval training', 6.0, 8.0, 12.0, TRUE, FALSE),
('Dancing', 'cardio', 'Various dance workouts', 4.0, 6.0, 8.0, TRUE, FALSE),
('Stretching', 'flexibility', 'Flexibility exercises', 2.0, 2.5, 3.0, FALSE, FALSE),
('Sports', 'sports', 'Various sports activities', 4.0, 6.0, 8.0, TRUE, FALSE);

-- Insert common foods
INSERT INTO food_entries (name, brand, serving_size, serving_unit, calories, protein_g, carbohydrates_g, fat_g, fiber_g, category, is_verified) VALUES
('Apple', NULL, 180, 'g', 95, 0.5, 25, 0.3, 4.4, 'fruits', 1),
('Banana', NULL, 118, 'g', 105, 1.3, 27, 0.4, 3.1, 'fruits', 1),
('Chicken Breast', NULL, 100, 'g', 165, 31, 0, 3.6, 0, 'protein', 1),
('Brown Rice', NULL, 158, 'g', 216, 5, 45, 1.8, 3.5, 'grains', 1),
('Broccoli', NULL, 91, 'g', 31, 2.5, 6, 0.4, 2.4, 'vegetables', 1),
('Salmon', NULL, 100, 'g', 208, 20, 0, 13, 0, 'protein', 1),
('Egg', NULL, 50, 'g', 78, 6, 0.6, 5, 0, 'protein', 1),
('Greek Yogurt', NULL, 170, 'g', 100, 17, 6, 0.7, 0, 'dairy', 1),
('Oatmeal', NULL, 40, 'g', 150, 5, 27, 2.5, 4, 'grains', 1),
('Almonds', NULL, 28, 'g', 164, 6, 6, 14, 3.5, 'nuts', 1);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_goals_updated_at BEFORE UPDATE ON user_goals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_food_entries_updated_at BEFORE UPDATE ON food_entries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_nutrition_logs_updated_at BEFORE UPDATE ON nutrition_logs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_exercise_logs_updated_at BEFORE UPDATE ON exercise_logs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_water_logs_updated_at BEFORE UPDATE ON water_logs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_walking_sessions_updated_at BEFORE UPDATE ON walking_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_food_scans_updated_at BEFORE UPDATE ON food_scans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
