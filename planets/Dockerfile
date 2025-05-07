FROM python:3.10-slim
WORKDIR /app

COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y libgomp1 && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python", "get_planets.py", "--test-mode"]