# ===============================
# Base Image
# ===============================
FROM python:3.10-slim

# ===============================
# Environment Settings
# ===============================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ===============================
# System Dependencies
# ===============================
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ===============================
# Working Directory
# ===============================
WORKDIR /app

# ===============================
# Install Python Dependencies
# ===============================
COPY backend/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ===============================
# Copy Project Files
# ===============================
COPY backend /app

# ===============================
# Expose Port
# ===============================
EXPOSE 8000

# ===============================
# Health Check (VERY IMPORTANT)
# ===============================
HEALTHCHECK CMD curl --fail http://localhost:8000 || exit 1

# ===============================
# Run App
# ===============================
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
