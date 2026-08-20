FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
RUN pip install fastapi uvicorn httpx pydantic
COPY . .
EXPOSE 8004
CMD ["uvicorn", "extract:app", "--host", "0.0.0.0", "--port", "8004"]
