# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the poetry lock and pyproject.toml
COPY pyproject.toml poetry.lock* /app/

# Install poetry
RUN pip install --no-cache-dir poetry

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Copy the rest of the application code
COPY . .

# Define the entry point for the container
ENTRYPOINT ["poetry", "run", "python", "app/main.py"]
docker build -t fast-python-mongo-demo-app .
docker run --env-file .env fast-python-mongo-demo-app