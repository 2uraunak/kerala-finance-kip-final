FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
RUN pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic
COPY . .
EXPOSE 8007
CMD ["uvicorn", "analytics:app", "--host", "0.0.0.0", "--port", "8007"]
