# 1. Modern Python image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. System dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy and Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy all files
COPY . .

# 6. Streamlit Cloud Config
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# 7. Expose Port
EXPOSE 10000

# 8. Run Streamlit on Render's Port
# Ye command "executable file not found" error ko fix karegi
CMD ["sh", "-c", "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"]
