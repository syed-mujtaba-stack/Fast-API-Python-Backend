# Friendly Video Sphere - Backend

This is the backend service for the Friendly Video Sphere application, built with FastAPI.

## Getting Started

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- (Optional) PostgreSQL for production

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd friendly-video-sphere/backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Update the variables in `.env` as needed

### Running the Application

#### Development
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

#### Production
For production, you might want to use a production ASGI server like Uvicorn with Gunicorn:

```bash
pip install gunicorn
gunicorn -k uvicorn.workers.UvicornWorker main:app
```

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── .env                    # Environment variables
├── main.py                 # Main application file
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .gitignore             # Git ignore file
```

## Development

### Code Style

This project uses `black` for code formatting and `isort` for import sorting.

```bash
# Install development dependencies
pip install black isort

# Format code
black .


# Sort imports
isort .
```

### Testing

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest
```

## Deployment

### Docker

Build and run with Docker:

```bash
docker build -t friendly-video-sphere-backend .
docker run -d --name fvs-backend -p 8000:8000 friendly-video-sphere-backend
```

### Environment Variables

See `.env.example` for all available environment variables.

## License

[Your License Here]
