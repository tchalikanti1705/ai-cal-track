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

## Getting Started

```bash
# Clone the repository
git clone https://github.com/tchalikanti1705/ai-cal-track.git
cd ai-cal-track

# Start all services with Docker
docker-compose up -d

# Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

MIT License
