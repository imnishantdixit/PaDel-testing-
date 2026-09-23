FROM python:3.11-slim

# Install Java Runtime Environment for PaDEL engine
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and PaDEL JAR engine
COPY app.py .
COPY services ./services
COPY padel ./padel
COPY data ./data
COPY .streamlit ./.streamlit

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
