FROM python:3.10-slim

WORKDIR /app

# Install basic system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire codebase
COPY . .

# Set the entrypoint to the main python script
ENTRYPOINT ["python", "main.py"]

# Default command if none is provided
CMD ["--prompt", "Patrol the warehouse twice", "--mock-llm"]
