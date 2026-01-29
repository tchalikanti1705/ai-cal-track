# AI Food Tracking

A health and nutrition tracking platform with AI-powered food recognition.

## Features

- Calorie intake tracking with detailed macro information
- Water intake tracking
- Insights and analytics with charts and trends
- AI-powered food scanning

## Architecture

### Frontend
- React 18 with TypeScript
- Vite build tool
- Tailwind CSS for styling
- Zustand for state management
- Chart.js for data visualization

### Backend
- FastAPI (Python)
- PostgreSQL database
- SQLAlchemy ORM
- JWT authentication
- OpenAI GPT-4 Vision for food recognition

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




