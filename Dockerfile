# 1. Use a modern, slim Python version for efficiency [cite: 13]
FROM python:3.11-slim

# 2. Set working directory [cite: 15]
WORKDIR /app

# 3. Install system dependencies for OpenCV, MediaPipe, and Streamlit [cite: 13, 17]
# libgl1 aur libglib2.0-0 zaroori hain image processing ke liye
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements and install to leverage Docker cache [cite: 12]
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code [cite: 16, 21]
COPY . .

# 6. Streamlit Environment Variables for Cloud Deployment [cite: 14]
# Headless mode ensures it runs without a GUI [cite: 19]
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# 7. Expose the port (Informational for Render) [cite: 24]
EXPOSE 10000

# 8. Final Command: Binding Streamlit to Render's dynamic $PORT
# Ye line "Port Scan Timeout" error ko fix karegi 
CMD ["sh", "-c", "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"]
