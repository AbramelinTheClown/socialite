FROM python:3.10-slim
RUN pip install poetry==1.8.2
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main
COPY . .
CMD ["python", "tts_processor.py"]