# Security & Data Isolation Model

As per the hackathon prompt, a critical requirement is maintaining strict enterprise data isolation. Cloud-based LLMs cannot be used for sensitive government financial data.

## 1. 100% Local & Air-gapped Execution
- **LLMs:** We use locally hosted models (like Llama-3-8B via Ollama). No prompts, embeddings, or documents are ever sent to external APIs like OpenAI or Anthropic.
- **Embeddings:** Vector embeddings are generated locally using the `sentence-transformers` library running inside the ingestion container.
- **Data Storage:** PostgreSQL and ChromaDB run in isolated Docker networks. They do not expose ports to the host machine.

## 2. Role-Based Access Control (RBAC)
The platform enforces strict JWT-based access control with three primary roles:
1. **Admin:** Full access. Can upload, delete, and supersede documents.
2. **Analyst:** Can search, chat with the GST agent, and extract clauses. Cannot modify document lineage.
3. **Viewer:** Read-only search access. Cannot access restricted documents.

## 3. Restricted Document Handling
Documents can be flagged as `is_restricted` during ingestion. 
- The search service filters out restricted documents at the database level for any user without the appropriate clearance level, ensuring sensitive budget drafts or classified memos are never surfaced in RAG contexts or search results.
