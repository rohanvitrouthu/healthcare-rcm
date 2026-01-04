FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (e.g., for pyarrow/pandas)
RUN apt-get update && apt-get install -v -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Command to run the processor
CMD ["python", "main.py"]

