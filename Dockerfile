# Guardian A2A Orchestrator Dockerfile - Production Ready
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV DEBUG=false

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ /app/backend/
COPY samples/ /app/samples/
COPY tests/ /app/tests/

# Create non-root user
RUN useradd --create-home --shell /bin/bash guardian \
    && chown -R guardian:guardian /app
USER guardian

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Health check - check if the FastAPI server is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ag-ui/health || exit 1

# Run the AG-UI backend server
CMD ["python", "-m", "uvicorn", "backend.ag_ui_backend:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
