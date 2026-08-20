# Test Scenarios & Known Limitations

## Core Scenarios Handled Successfully

1. **Superseded Document Avoidance:**
   - *Test:* Search for "Dearness Allowance 2023".
   - *Result:* Retrieves GO 45/2023, but attaches a strict `SUPERSEDED` warning and points to GO 12/2024.

2. **RAG Grounding & Hallucination Prevention:**
   - *Test:* Ask GST Agent "What is the capital of France?" or "What is the GST rate for spaceships?"
   - *Result:* Agent refuses to answer, stating the information is not present in official circulars.

3. **Hybrid Search Superiority:**
   - *Test:* Search for exact bureaucratic identifiers (e.g. `GO(Ms)No.45/2023/Fin`).
   - *Result:* Semantic search fails on identifiers, but the BM25 keyword search catches it and boosts it to the top via RRF.

## Known Limitations & Future Improvements

1. **OCR on Malayalam Text:**
   - Currently, Tesseract struggles with older, heavily degraded scanned Malayalam PDFs. Fine-tuning an OCR model on Malayalam government fonts is required for production.

2. **Table Extraction:**
   - Complex financial tables in budget documents lose structural formatting during semantic chunking. Implementing a multimodal vision model (like LLaVA) to extract tables as markdown would significantly improve table comprehension.

3. **Hardware Constraints:**
   - To deploy a 70B parameter reasoning model, the department will need dedicated inference clusters rather than standard consumer hardware.
