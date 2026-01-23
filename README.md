# 🥗 AI Food Tracking

A comprehensive health and nutrition tracking platform with AI-powered food recognition.

## Features

- **🔐 User Authentication** - Secure login/registration with JWT tokens
- **📊 Dashboard** - Overview of daily nutrition, water, steps, and exercise
- **🍎 Nutrition Tracking** - Log meals with detailed macro information
- **💧 Water Tracking** - Track daily hydration with quick-add buttons
- **🏃 Exercise Logging** - Log workouts with calorie burn calculations
- **👣 Walking/Steps** - Track daily steps and walking sessions
- **📸 AI Food Scanning** - Take a photo of food to automatically identify and log it
- **📈 Insights & Analytics** - Charts and trends for your health data

## Tech Stack

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Zustand** - State management
- **Chart.js** - Data visualization
- **React Hook Form** - Form handling
- **Framer Motion** - Animations

### Backend
- **FastAPI** - Python web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **JWT** - Authentication
- **OpenAI GPT-4 Vision** - Food recognition (optional)

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Docker (optional)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/ai-food-tracking.git
cd ai-food-tracking

# Start all services
docker-compose up -d

# Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Initialize database
psql -U postgres -c "CREATE DATABASE food_tracking;"
psql -U postgres -d food_tracking -f database/schema.sql

# Run the server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Environment Variables

### Backend (.env)

```env
# Application
APP_NAME="AI Food Tracking"
DEBUG=true
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/food_tracking

# JWT
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (for food scanning)
OPENAI_API_KEY=your-openai-api-key
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## API Documentation

When running in development mode, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
ai-food-tracking/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Config, security, logging
│   │   ├── db/            # Database connection
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── database/          # SQL scripts
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── stores/        # Zustand stores
│   │   ├── types/         # TypeScript types
│   │   └── App.tsx        # Main app
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## Features Roadmap

- [ ] Meal planning and recipes
- [ ] Barcode scanning
- [ ] Social features and challenges
- [ ] Wearable device integrations
- [ ] Personalized meal recommendations
- [ ] Export data to CSV/PDF
- [ ] Dark mode

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.
