.PHONY: up down seed test logs pull-model clean build

# Start all services
up:
	docker-compose up -d --build
	@echo "✅ Kerala Finance KIP is running at http://localhost"
	@echo "   API Gateway: http://localhost:8000/docs"
	@echo "   Frontend:    http://localhost:3000"
	@echo "   MinIO:       http://localhost:9001"

# Stop all services
down:
	docker-compose down

# Pull LLM model into Ollama (run after 'make up')
pull-model:
	docker exec kip-ollama ollama pull llama3.2
	@echo "✅ llama3.2 model ready"

# Seed sample documents and mock users
seed:
	docker exec kip-api-gateway python scripts/seed_users.py
	docker exec kip-ingestion python scripts/seed_documents.py
	@echo "✅ Sample documents and users seeded"

# Run automated tests
test:
	docker exec kip-api-gateway python -m pytest tests/ -v --tb=short
	@echo "✅ All tests complete"

# View logs for a specific service (usage: make logs SERVICE=api-gateway)
logs:
	docker-compose logs -f $(SERVICE)

# Clean all volumes (WARNING: destroys all data)
clean:
	docker-compose down -v
	@echo "✅ All volumes cleaned"

# Build only (no start)
build:
	docker-compose build
