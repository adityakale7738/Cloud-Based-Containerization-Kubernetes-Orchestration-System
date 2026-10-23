# ==============================================================================
# Dockerfile: Production-Ready Container for Cloud Demo App
# ==============================================================================

# Base image: Official lightweight Python 3.12 Debian slim
FROM python:3.12-slim AS runtime

# Set operational environment variables:
# 1. PYTHONUNBUFFERED=1 prevents stdout/stderr buffering for real-time logging
# 2. PYTHONDONTWRITEBYTECODE=1 prevents creating .pyc bytecode in the container
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000 \
    APP_VERSION=1.0.0

# Set container working directory
WORKDIR /app

# Security best practice: Create a non-root system user and group (UID 1000)
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/bash -m appuser

# Install Python dependencies first (leverages Docker cache layer)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy application source code
COPY app.py /app/app.py

# Set proper ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch from root to non-root user
USER appuser

# Expose internal application port
EXPOSE 5000

# Docker-level healthcheck for the container engine
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health').read()" || exit 1

# Production command using Gunicorn WSGI server (2 workers, 2 threads per worker)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
