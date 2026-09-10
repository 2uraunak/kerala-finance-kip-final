# Round 2 Demo Script — 8 Minutes
**Event:** TCS AI Club "Prompt to Impact" Hackathon — Round 2 Live Demo
**Date:** Tuesday, September 15, 2026, 3:00 PM IST
**Team:** Team 2 (Neuro Pulse)
**Use Case Title:** Finance Policy and Government Order Knowledge Intelligence Platform

---

> [!IMPORTANT]
> Rules: Do NOT say "Neuro Pulse" or "Kerala Finance KIP" during the demo. You are "Team 2" and the product is the **"Finance Policy and Government Order Knowledge Intelligence Platform"**.

> [!TIP]
> Pre-demo: Open Chrome (NOT Firefox). Log in as `admin` before your slot starts. Run `python scripts/demo_scenario.py` to confirm all checks pass. Keep the app at `http://localhost` on fullscreen.

---

## DEMO TIMELINE

```
[0:00 – 1:00]  INTRO        — Problem framing (1 slide on screen, not the app)
[1:00 – 3:30]  ACT 1        — The Superseded Order Trap (core demo)
[3:30 – 5:30]  ACT 2        — Policy Note Agent with human checkpoint
[5:30 – 7:00]  ACT 3        — Metadata classification + filters + access control
[7:00 – 8:00]  CLOSE        — Analytics + architecture summary
```

---

## [0:00 – 1:00] INTRO — The Problem

**Say:**
> "The Finance Department of Government of Kerala manages thousands of Government Orders, circulars, and notifications — many of which have been amended or superseded over the years. If an official searches for a DA rate and the system returns a 2-year-old superseded order as authoritative, it could cause a wrongful payment of crores in arrears. Our platform solves this — not just by retrieving documents, but by *proving* which version is authoritative and *why*."

*(Flip to the app. Start at the Dashboard.)*

---

## [1:00 – 3:30] ACT 1 — The Superseded Order Trap

> **Objective:** Show that the platform detects, warns, and routes past outdated GOs.

**Step 1.1 — Navigate to Search.**

**Step 1.2 — Type or SPEAK this query:**
> "What is the current Dearness Allowance rate for Kerala state government employees?"

*(Click the 🎙️ mic button to demonstrate voice input. Speak the query.)*

**Say while results load:**
> "We're using hybrid retrieval — ChromaDB vector search combined with BM25 keyword search, fused via Reciprocal Rank Fusion."

**Step 1.3 — Results appear. POINT TO:**
- The result showing `GO(Ms)No.45/2023/Fin` with a **🔴 SUPERSEDED** badge
- The lineage warning bar below it
- The AI-generated answer which explicitly says:

> *"⚠️ Warning: GO(Ms)No.45/2023/Fin has been SUPERSEDED by GO(Ms)No.112/2023/Fin dated 01.09.2023. The DA rate of 42% cited in GO 45 is no longer authoritative. The current applicable rate is 46%, effective from 01.07.2023 per GO(Ms)No.112/2023/Fin."*

**Say:**
> "Notice the system didn't just retrieve a result — it **intercepted** the outdated order, flagged it as superseded, resolved the correct active version, and explicitly warned the official not to use it. Every answer carries the source document, page number, status, and confidence score. This is *grounded* retrieval — not hallucination."

**Step 1.4 — Click on the Documents page. Show GO 45/2023:**
- Red left border
- 🔴 SUPERSEDED badge
- The red warning bar: *"SUPERSEDED: This order is no longer authoritative"*

**Step 1.5 — Click on GO 112/2023. Show:**
- ✅ ACTIVE badge
- `classification_confidence: ⚡ 98%` badge
- Summary showing it supersedes GO 45

---

## [3:30 – 5:30] ACT 2 — Policy Note Agent with Human Checkpoint

**Navigate to Policy Note Agent.**

**Say:**
> "Now watch the agent draft a compliant policy note citing *only* the authoritative version."

**Step 2.1 — Enter this subject:**
> "Draft a policy note on Dearness Allowance disbursement for Q1 2024"

**Step 2.2 — Click Execute/Draft.**

*While it runs, say:*
> "The agent runs a three-step workflow: Retrieve → Verify → Draft. In the verify step, it specifically checks lineage status — if any retrieved document is superseded, it is excluded before the draft is generated."

**Step 2.3 — The draft appears. POINT OUT:**
- The draft cites `GO(Ms)No.112/2023/Fin` (the ACTIVE one, DA @ 46%)
- It does NOT cite GO 45/2023
- Source passages are shown with page numbers
- The **"Approve this policy note?"** human checkpoint button appears

**Say:**
> "Before this note can be finalized, it requires a human approval checkpoint. This is enterprise-grade governance — no AI-generated policy note bypasses human review."

---

## [5:30 – 7:00] ACT 3 — Classification + Filters + Access Control

**Navigate to Document Library.**

**Step 3.1 — Show Auto-Classification:**
- Point to the `⚡ 98%` and `⚡ 97%` confidence badges
- Click "Correct Classification" on any document
- Say: *"If the auto-classification is wrong, an admin can correct it with a documented reason — fully auditable."*

**Step 3.2 — Show Filters:**
- Select Year: **2023**, Status: **Active**
- Show only active 2023 GOs appear
- Select Status: **Superseded** — show only GO 45 appears
- Select something that returns zero results: Year **2020**, Type **GST Policy**
- Show the helpful empty-result message: *"No GST policies found for 2020. Try adjusting your filters."*

**Step 3.3 — Show RBAC (Access Control):**
- Click top-right user icon → Switch to **Viewer** role (or log out, log in as viewer)
- Navigate to Documents
- The **Restricted Audit Report** is completely invisible
- Try to access it via direct URL → Show **403 Access Denied** response
- Switch back to Admin

**Say:**
> "Three-tier role-based access — Admin, Analyst, and Viewer — with document-level restrictions. The audit report is completely invisible to non-admins."

---

## [7:00 – 8:00] CLOSE — Analytics + Architecture

**Navigate to Analytics.**

**Step 4.1 — Point to Operational Metrics:**
- **🚫 Superseded Blocks** counter — "This is how many times the platform intercepted outdated orders"
- **🔒 Access Denied** counter — "RBAC enforcement events"
- **⚡ Avg Response** — "End-to-end retrieval latency"

**Step 4.2 — Show Audit Trail:**
- Scroll to the audit table
- Point to the full tamper-evident log
- Say: *"Every action — every search, every access denial, every policy note draft — is logged here with timestamp, user, role, IP, and latency."*

**Step 4.3 — Close with architecture:**
> "This entire platform runs 100% locally. No document, no query, no sensitive government data ever leaves the local environment. The LLM runs on Ollama, the embeddings on ChromaDB, the search on BM25+RRF — all inside Docker containers that start with a single `make up` command. It is reproducible, air-gapped, and enterprise-ready."

---

## KEY PHRASES TO USE (Jury-targeted)

| Phrase | Use When |
|--------|----------|
| "Grounded retrieval — not hallucination" | After showing the source citation |
| "Human-in-the-loop checkpoint" | When the approval button appears |
| "Lineage-aware — superseded orders are intercepted, not returned as authoritative" | In Act 1 |
| "Air-gapped, 100% local processing" | In closing |
| "Contract-faithful e-Office integration" | If asked about integration |
| "Tamper-evident, append-only audit trail" | In analytics section |

---

## Q&A Anticipation (4 minutes)

**Q: "How does it know a GO is superseded?"**
> "Two ways: at ingestion time, our classifier detects supersession language in the text and flags it automatically. Administrators can also explicitly set the superseded_by relationship through the lineage API — which creates a directed chain from old to new."

**Q: "What if Ollama or the LLM is slow?"**
> "The retrieval pipeline — BM25 + ChromaDB — returns results in under 150ms. The LLM generation adds latency, but in production we would use quantized models or GPU acceleration. For this POC, the local Llama 3.2 model runs entirely on CPU."

**Q: "Is this production-ready?"**
> "This is a production-grade architecture in a POC footprint. The same Docker Compose stack can be migrated to Kubernetes with horizontal scaling of the microservices. The services are already stateless — the database and vector store are the only stateful components."

**Q: "What about Malayalam documents?"**
> "Currently optimized for English. Multilingual embedding models and Malayalam-capable LLMs are the first item on our future roadmap."
