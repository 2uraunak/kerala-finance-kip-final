# Kerala Finance KIP — Pitch Deck Content

This document contains the exact text and layout for your 9-slide PowerPoint presentation. 

---

## Slide 1: Title Slide
**Title:** Kerala Finance KIP (Knowledge Intelligence Platform)
**Subtitle:** Enterprise Document Intelligence for the Finance Department, Govt. of Kerala
**Team:** [Your Team Name / Names]
**Logo:** Add the official Kerala Government logo or a generic AI/Finance icon.

---

## Slide 2: The Problem
**Title:** The Challenge in Finance Document Management
**Content:**
* **Volume & Complexity:** Thousands of Government Orders, circulars, budget docs, and GST policies across years and formats.
* **Lineage & Supersession:** High risk of using superseded orders, affecting financial decisions and file processing.
* **Time-Intensive Workflow:** Officials spend hours manually searching, extracting clauses, and drafting policy notes.
* **Security Constraints:** Highly sensitive financial data cannot be sent to public cloud AI APIs.

---

## Slide 3: Our Solution
**Title:** A 100% Local, AI-Powered Knowledge Platform
**Content:**
* **Intelligent Search:** Hybrid semantic & keyword search with verifiable source citations.
* **Document Lineage Tracker:** Automatically resolves active vs. superseded orders.
* **Automated Extraction:** Instantly pulls structured clauses and financial figures from PDFs.
* **Agentic Assistance:** AI agents that help research GST policies and draft official policy notes.
* **Enterprise Security:** Fully local deployment (Ollama LLM) with Role-Based Access Control and tamper-evident audit logs.

---

## Slide 4: System Architecture
**Title:** Enterprise Architecture
**Visual:** *(Paste the `docs/architecture.png` image here)*
**Talking Points:**
* Divided into Presentation, API Gateway, Microservices, and Data tiers.
* Uses FastAPI for robust backend services and React for the frontend.
* **Zero Cloud Leakage:** Uses a local Ollama instance (Llama 3.2) and local sentence-transformers.

---

## Slide 5: Data Flow
**Title:** Ingestion & Search Pipelines
**Visual:** *(Paste the `docs/data-flow.png` image here)*
**Talking Points:**
* **Ingestion:** Scans PDFs (using Tesseract OCR) → chunks text → embeds into ChromaDB.
* **Search:** Uses Reciprocal Rank Fusion (RRF) to combine vector search and BM25 keyword search.
* Every answer generated is filtered through the lineage service to exclude superseded documents.

---

## Slide 6: Key Feature: Source Review Labels
**Title:** Building Trust with Source Review Labels
**Content:**
* **The AI Hallucination Problem:** Generative AI cannot be trusted blindly in government finance.
* **Our Approach:** Every AI output includes a **Source Review Label**.
* **What it shows:**
  * Exact source document and page number.
  * Active/Superseded status indicator.
  * Confidence score of the extraction.

---

## Slide 7: Feature Demo
**Title:** Platform Capabilities
**Visuals:** *(Add 2-3 screenshots of the React frontend UI)*
* Screenshot 1: The Hybrid Search screen showing a cited answer.
* Screenshot 2: The Policy Note Drafter Agent showing the multi-step process.
* Screenshot 3: The Document Lineage tree.

---

## Slide 8: Evaluation & Quality
**Title:** Measured Accuracy & Code Quality
**Content:**
* **Automated Testing:** Pytest suite continuously measures search accuracy, lineage resolution, and access control.
* **Dockerized Deployment:** The entire 12-container system spins up with a single `docker compose up` command.
* **Auditability:** Every search, extraction, and login is recorded in an append-only SQLite audit log.

---

## Slide 9: Team & Roadmap
**Title:** Future Enhancements
**Content:**
* **Immediate Next Steps:** Pilot deployment on internal Finance Dept intranet.
* **Future Features:** 
  * Integration with e-Office workflow.
  * Multi-lingual support (Malayalam OCR).
* **Thank You!**
**Contact:** [Your Email / Team info]
