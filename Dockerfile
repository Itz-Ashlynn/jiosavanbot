# Use Python 3.11 slim image for better performance and smaller size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/downloads /app/logs

# Set proper permissions
RUN chmod +x -R /app

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash jiosaavn && \
    chown -R jiosaavn:jiosaavn /app
USER jiosaavn

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-80}/ || exit 1

# Expose the port (will be overridden by environment variable)
EXPOSE 80

# Set default command
CMD ["python3", "-m", "jiosaavn"]
