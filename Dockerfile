# Use the official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# System dependencies for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port (Streamlit defaults to 8501, or Render overrides it)
EXPOSE 8501

# Streamlit-specific config for Cloud execution
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Run the application
CMD ["streamlit", "run", "app.py"]
