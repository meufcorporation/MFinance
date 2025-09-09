# Multi-stage build for production
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
        git \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development
COPY . .
RUN mkdir -p logs media staticfiles && chmod 755 logs
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Production stage
FROM base as production
COPY . .

# Create non-root user
RUN groupadd -r mfinance && useradd -r -g mfinance mfinance

# Create necessary directories
RUN mkdir -p logs media staticfiles \
    && chown -R mfinance:mfinance /app \
    && chmod 755 logs

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Switch to non-root user
USER mfinance

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "mfinance.wsgi:application"]
