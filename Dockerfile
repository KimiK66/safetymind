# SafetyMind Dockerfile for Production Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY web/ ./web/
COPY data/ ./data/
COPY run.py .
COPY app.py .

# Create necessary directories
RUN mkdir -p /app/videos /app/logs

# Set environment variables
ENV PYTHONPATH=/app/src
ENV SAFETYMIND_HOST=0.0.0.0
ENV SAFETYMIND_PORT=8000
ENV SAFETYMIND_LOG_LEVEL=INFO

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["python", "run.py"]
