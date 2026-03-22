# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy package files first (better caching)
COPY pyproject.toml README.md LICENSE ./
COPY src/ src/

# Install the package with service dependencies
RUN pip install --no-cache-dir ".[service]"

# Copy the rest of the application
COPY . . 

# Expose port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
