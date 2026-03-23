# Use a more modern Python version
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Updated System dependencies for OpenCV and MediaPipe
# Removed the deprecated libgl1-mesa-glx and used libgl1 instead
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies (using --no-cache-dir saves RAM during build)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure the app uses the PORT variable provided by Render
# This fixes the "No open ports detected" issue
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Expose the port (informative only)
EXPOSE 8501

# Command to run the app
# We use 8501 here because you set the PORT variable to 8501 in Render Dashboard
CMD ["streamlit", "run", "app.py"]# Use a more modern Python version
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Updated System dependencies for OpenCV and MediaPipe
# Removed the deprecated libgl1-mesa-glx and used libgl1 instead
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies (using --no-cache-dir saves RAM during build)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure the app uses the PORT variable provided by Render
# This fixes the "No open ports detected" issue
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Expose the port (informative only)
EXPOSE 8501

# Command to run the app
# We use 8501 here because you set the PORT variable to 8501 in Render Dashboard
CMD ["streamlit", "run", "app.py"]
