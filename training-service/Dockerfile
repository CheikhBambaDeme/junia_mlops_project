FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/models/artifacts

# Expose port
EXPOSE 8000

# Model will be loaded at startup via FastAPI lifespan
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
