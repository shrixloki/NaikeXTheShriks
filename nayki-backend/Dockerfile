FROM python:3.12-slim

# Set runtime optimization environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    API_PORT=8000

# Install build dependencies and tools (libpq-dev for postgres connection)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency configuration
COPY pyproject.toml /app/

# Install standard dependencies and developer dependencies (for tests)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir . && \
    pip install --no-cache-dir ".[dev]"

# Copy all codebase files
COPY . /app/

# Expose API service port
EXPOSE 8000

# Command to launch hot-reloading development server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
