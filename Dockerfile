# 1. Use a modern, slim Python version
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies for OpenCV/MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy and Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy all project files
COPY . .

# 6. Streamlit Environment Variables
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# 7. Expose the main Render Port
EXPOSE 10000

# 8. THE BRAIN FIX: Start Backend (8000) and Frontend ($PORT) together
# Backend ko background (&) mein dala hai taaki dono ek saath chalein
CMD uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port $PORT --server.address 0.0.0.0
