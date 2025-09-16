# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY befriends/ ./befriends/
COPY scripts/ ./scripts/

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "befriends.app:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
