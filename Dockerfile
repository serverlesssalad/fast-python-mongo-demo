# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the poetry files and install dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && \
    poetry install --no-root --no-dev

# Copy the rest of the application files
COPY app/ ./app/
COPY .env ./

# Set the entrypoint to your main application
ENTRYPOINT ["poetry", "run", "python", "./app/main.py"]
   docker build -t flexmongo .
   docker run --env-file .env flexmongo