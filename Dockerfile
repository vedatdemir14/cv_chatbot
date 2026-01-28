FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p data

# Expose API port
EXPOSE 8000

# Run ingestion on startup (optional - comment out if index is pre-built)
# RUN python ingest.py

# Start the API server
CMD ["python", "app.py"]



