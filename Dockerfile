# Use an official Python base image with Python 3.12
FROM python:3.12-slim

# Working Directory
WORKDIR /app

# Copy Files
COPY . /app

# Step 4: Install Poetry
RUN pip install poetry

# Step 5: Disable Virtual Environments
RUN poetry config virtualenvs.create false

# Step 6: Install Dependencies
RUN poetry install --no-dev

# Step 7: Expose Port
EXPOSE 8000

# Step 8: CMD to Run App
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]