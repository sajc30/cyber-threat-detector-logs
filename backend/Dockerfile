# Multi-stage build for production-ready backend
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .
COPY requirements.txt ./global-requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r global-requirements.txt

# Development stage
FROM base as development
ENV FLASK_ENV=development
COPY backend/ .
USER appuser
EXPOSE 5000 5001
CMD ["python", "app.py"]

# Production stage
FROM base as production
ENV FLASK_ENV=production

# Copy application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p logs data artifacts && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/api/health || exit 1

# Expose ports
EXPOSE 5000 5001

# Default command
CMD ["python", "app_simple.py"] 