# Use the official Python image as the base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the necessary files for Poetry
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install dependencies from Poetry
RUN poetry install --no-root --no-dev

# Copy the rest of the application files
COPY . .

# Set the entry point to run your application
ENTRYPOINT ["python", "app/main.py"]