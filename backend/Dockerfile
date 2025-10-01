# Use Python 3.11 slim image
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Development target
FROM base AS development

# Install development dependencies
RUN pip install --no-cache-dir flask[dotenv] watchdog

# Expose port
EXPOSE 5001

# Run with Flask development server for hot reloading
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001", "--debug"]

# Production target
FROM base AS production

# Copy application code
COPY . .

# Expose port
EXPOSE 5001

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]
