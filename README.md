# TradeCircle

A full-stack trading application with React frontend and Flask backend.

## Project Structure

```
tradecircle/
├── frontend/           # React application
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── backend/            # Flask API
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Features

- **Frontend (React)**:
  - Modern React application with hooks
  - Trade management interface
  - Real-time data display
  - Responsive design
  - Form validation

- **Backend (Flask)**:
  - RESTful API endpoints
  - CORS enabled for frontend communication
  - Trade CRUD operations
  - JSON data exchange
  - Health check endpoint

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Running with Docker (Recommended)

#### Development Mode (with Hot Reloading)

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd tradecircle
   ```

2. Build and run in development mode:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:3000 (React dev server with hot reloading)
   - Backend API: http://localhost:5001 (Flask debug mode with auto-reload)

#### Production Mode

1. Run the production build:
   ```bash
   docker-compose -f docker-compose.prod.yml up --build
   ```

2. Access the application:
   - Frontend: http://localhost:3000 (Nginx serving optimized build)
   - Backend API: http://localhost:5001 (Gunicorn WSGI server)

### Running Locally for Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/trades` - Get all trades
- `POST /api/trades` - Create a new trade
- `DELETE /api/trades/<id>` - Delete a trade

## Sample Trade Object

```json
{
  "id": 1,
  "symbol": "AAPL",
  "quantity": 100,
  "price": 150.50,
  "type": "buy",
  "timestamp": "2025-09-29T10:00:00Z"
}
```

## Development

### Hot Reloading Setup

The development Docker setup includes:
- **Frontend**: React development server with hot module replacement
- **Backend**: Flask debug mode with automatic code reloading
- **Volume Mapping**: Source code is mounted into containers for real-time updates

### Development Workflow

1. Start development environment:
   ```bash
   docker-compose up
   ```

2. Make changes to your code - the application will automatically reload:
   - Frontend changes in `frontend/src/` trigger instant React hot reloads
   - Backend changes in `backend/` trigger Flask auto-restart

3. Access logs:
   ```bash
   docker-compose logs -f frontend  # Frontend logs
   docker-compose logs -f backend   # Backend logs
   ```

### Adding New Features

1. Backend: Add new routes in `backend/app.py`
2. Frontend: Create new components in `frontend/src/`
3. Update this README with new API endpoints

### Testing

The application includes basic error handling and form validation. For production use, consider adding:
- Unit tests for both frontend and backend
- Integration tests
- Database integration (currently uses in-memory storage)
- Authentication and authorization
- Data persistence

## Docker Commands

### Development Commands
```bash
# Build and start development services with hot reloading
docker-compose up --build

# Start development services in background
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f frontend
docker-compose logs -f backend

# Stop development services
docker-compose down

# Rebuild specific service
docker-compose build backend
docker-compose build frontend
```

### Production Commands
```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up --build

# Start production services in background
docker-compose -f docker-compose.prod.yml up -d

# Stop production services
docker-compose -f docker-compose.prod.yml down

# Remove volumes (reset data)
docker-compose down -v
```

## Environment Variables

### Frontend
- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:5001/api)
- `CHOKIDAR_USEPOLLING` - Enable polling for file changes (development)
- `WATCHPACK_POLLING` - Enable webpack polling (development)

### Backend
- `PORT` - Server port (default: 5001)
- `FLASK_ENV` - Flask environment (development/production)
- `FLASK_DEBUG` - Enable Flask debug mode (development)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
