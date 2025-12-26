# Build Step 1: Build the React Frontend
FROM node:18 as build-step
WORKDIR /app-frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
# Remove the homepage field to ensure relative paths work
RUN npm pkg delete homepage
RUN npm run build

# Build Step 2: Setup the Python Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (FFmpeg)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy Backend Dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# Explicitly upgrade yt-dlp to the absolute latest version
RUN pip install --no-cache-dir --upgrade yt-dlp

# Copy Backend Code
COPY backend/ .

# Copy Built Frontend from Step 1 to a folder named 'client_build'
COPY --from=build-step /app-frontend/build ./client_build

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:10000", "--timeout", "120", "app:app"]