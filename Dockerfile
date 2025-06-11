FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# First install pip and poetry
RUN pip install --upgrade pip && \
    pip install poetry==2.1.2

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install project dependencies (including Celery)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --all-extras

# Verify Celery is installed
RUN python -m pip list | grep celery

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
