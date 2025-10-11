# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install gcc and python3-dev
RUN apt-get update && apt-get install -y gcc python3-dev

# Install poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app

# Copy Poetry's definition files
COPY pyproject.toml poetry.lock /app/

# Copy Poetry's definition files
COPY pyproject.toml poetry.lock README.md /app/

# Copy the main module
COPY src /app/src

# Copy the test files
COPY tests /app/tests
COPY pytest.ini /app

# Force poetry to create virtual environment under the same folder
RUN poetry config virtualenvs.in-project true

# Install dependencies using Poetry
RUN poetry install 

# Make port 8765 available to the world outside this container
EXPOSE 8765

# Start with an interactive shell
CMD ["bash"]