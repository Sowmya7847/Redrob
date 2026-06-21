FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-download and cache model weights during docker build phase
RUN python download_model.py

EXPOSE 10000

CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
