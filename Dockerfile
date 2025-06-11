FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry==2.1.2

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --all-extras

# Verify Celery is installed
RUN python -m pip list

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
