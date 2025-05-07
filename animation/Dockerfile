FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y \
    libgl1 \
    libgomp1 \
    fonts-liberation \
    fonts-noto-color-emoji && \
    pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium && \
    playwright instdocker run --help'-deps chromium && \
    rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python", "build_scene.py", "--test-mode"]