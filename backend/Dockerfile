# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/ /app/

# Install python deps
# If backend has its own requirements.txt, prefer it; otherwise use project root
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt || true
# Also attempt to install backend-specific service deps
RUN python -m pip install --no-cache-dir fastapi uvicorn[standard] PyJWT bcrypt python-dotenv openai

# Expose port
EXPOSE 8000

# Default env
ENV HOST=0.0.0.0 PORT=8000

# Run app
CMD ["python", "-c", "import uvicorn, os; uvicorn.run('main:app', host=os.getenv('HOST','0.0.0.0'), port=int(os.getenv('PORT','8000')))" ]