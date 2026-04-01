FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Set PYTHONPATH to include the Django project directory
ENV PYTHONPATH=/app/academor:$PYTHONPATH

# Install system dependencies (gettext əlavə edildi)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv
RUN uv pip sync uv.lock --system || uv pip install --system -e .

# Copy project
COPY . .

# Create entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "120", "--chdir", "academor", "academor.wsgi:application"]