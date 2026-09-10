FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY mock_adapter.py .
CMD ["uvicorn", "mock_adapter:app", "--host", "0.0.0.0", "--port", "8010"]
