FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (if any needed, none for now)

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Command to run the extractor
CMD ["python", "main.py"]
