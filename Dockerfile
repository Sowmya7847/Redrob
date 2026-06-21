FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-download and cache model weights during docker build phase
RUN python download_model.py

EXPOSE 10000

CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
