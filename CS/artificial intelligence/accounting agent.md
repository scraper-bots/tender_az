# 1) OCR POC plan & benchmark matrix — goal, test design, acceptance criteria

## Goal

Quickly evaluate and choose an OCR/document-understanding approach for invoice/receipt extraction with reliable field extraction (date, supplier, total, VAT, invoice number, line items). Run a 2–3 week POC on representative samples to decide whether to use a managed cloud OCR (faster, higher accuracy in complex layouts) or an open-source pipeline (lower cost, more control). ([unstract.com](https://unstract.com/blog/best-pdf-ocr-software/?utm_source=chatgpt.com "Best OCR Software in 2025 | PDF OCR Tool Comparison ..."), [skillup.ccccloud.com](https://skillup.ccccloud.com/2025/06/17/ai-document-analysis-tools-comparing-aws-textract-vs-azure-form-recognizer/?utm_source=chatgpt.com "Comparing AWS Textract vs Azure Form Recognizer – SkillUp"))

## Success criteria (POC exit criteria)

- **Field-level extraction accuracy** (precision/recall) ≥ 90% for top-level fields (invoice number, date, total) on typical supplier invoices.
    
- **Line-item detection accuracy** (line-level extraction) ≥ 80% for multi-line invoices (if line-items are required).
    
- **Throughput**: median per-document processing latency ≤ 5s for single synchronous requests (as per SRS target).
    
- **False positive rate on invoice detection** (non-invoice inputs) < 5%.
    
- **Ease of integration**: available SDK/REST API and clear error handling within 2 working days of exploration.
    
- **Cost estimate**: 6-12 month cost projection with expected monthly volume must be produced.
    

## Dataset preparation

- **Sample size**: 150–200 documents total (minimum 50 for initial quick test, 150+ for thorough benchmark).
    
    - 60% typical invoices (various suppliers)
        
    - 20% complex invoices with multi-column / nested tables and line items
        
    - 10% receipts / small documents (low-resolution scans, mobile photos)
        
    - 10% negative examples (non-invoice PDFs, blank pages, malformed images)
        
- **Metadata required per sample**: ground-truth JSON with canonical fields (invoice_number, date, supplier_name, subtotal, tax, total, currency, line_items array). Use an agreed canonical schema.
    
- **Anonymization**: replace personal or sensitive data where required by law before sending to any 3rd-party provider.
    

## Tools to evaluate (initial shortlist)

- **Managed**: Azure Form Recognizer (Document Intelligence), Google Document AI, AWS Textract (managed services are recommended when accuracy on complex layouts is critical). ([unstract.com](https://unstract.com/blog/best-pdf-ocr-software/?utm_source=chatgpt.com "Best OCR Software in 2025 | PDF OCR Tool Comparison ..."), [skillup.ccccloud.com](https://skillup.ccccloud.com/2025/06/17/ai-document-analysis-tools-comparing-aws-textract-vs-azure-form-recognizer/?utm_source=chatgpt.com "Comparing AWS Textract vs Azure Form Recognizer – SkillUp"))
    
- **Open-source baseline**: Tesseract / PaddleOCR + custom line-item parsing (for cost-limited or on-premise requirements).
    

## Metrics & measurement

Measure these for each tool on the test dataset:

1. **Field extraction metrics**
    
    - Precision, Recall, F1 for each field (invoice_number, date, total, tax, supplier_name)
        
2. **Line-item metrics**
    
    - Line recall (fraction of true line items extracted)
        
    - Line precision (fraction of predicted lines that are correct)
        
3. **Document-level metrics**
    
    - % documents fully parsed (all required fields present and validated)
        
4. **Latency**
    
    - Median and 95th percentile per-document processing time
        
5. **Operational metrics**
    
    - Error rate, retry count, rate limits, SDK stability
        
6. **Cost**
    
    - $ per page (estimated at expected production volume) and projected monthly cost.
        
7. **Integration & security**
    
    - Support for private deployment/data residency, encryption at rest/in transit
        

## Benchmark matrix (example)

|Tool|Field F1 (avg)|Line-item F1|Median latency|Supports custom training|Data residency options|Estimated $/page|Notes|
|---|--:|--:|--:|--:|--:|--:|---|
|Azure Form Recognizer|0.90–0.94 ([unstract.com](https://unstract.com/blog/best-pdf-ocr-software/?utm_source=chatgpt.com "Best OCR Software in 2025 \| PDF OCR Tool Comparison ..."))|0.82–0.87|~1.5–3s|Yes (custom models)|Azure regions (sovereign options)|$$$|Strong table handling|
|Google Document AI|0.88–0.92|0.78–0.84|~1.5–3s|Yes|GCP regions|$$$|Good for multilingual docs|
|AWS Textract|0.80–0.90|0.75–0.82|~2–4s|Limited custom|AWS regions|$$|Good for structured docs|
|Tesseract + custom|0.60–0.85|0.40–0.70|variable|Fully custom|On-prem possible|$ (infra)|Cost-effective, more engineering|

_(Populate exact numbers after running the POC on your 150–200 sample set. The ranges above reflect typical comparative reports.)_ ([unstract.com](https://unstract.com/blog/best-pdf-ocr-software/?utm_source=chatgpt.com "Best OCR Software in 2025 | PDF OCR Tool Comparison ..."), [skillup.ccccloud.com](https://skillup.ccccloud.com/2025/06/17/ai-document-analysis-tools-comparing-aws-textract-vs-azure-form-recognizer/?utm_source=chatgpt.com "Comparing AWS Textract vs Azure Form Recognizer – SkillUp"))

## POC step-by-step (2–3 weeks)

**Week 0 (plan & dataset)**

- Identify and collect 150–200 samples, label ground-truth JSON. Assign SME for label validation.
    
- Define canonical schema and field matching rules.
    

**Week 1 (quick runs: 50 samples)**

- Run each managed service on 50-sample subset. Extract raw outputs and map to canonical schema.
    
- Compute field-level metrics, note error modes (table detection failures, OCR noise, rotated pages).
    

**Week 2 (full benchmark: 150–200 samples)**

- Run full benchmark for top 2 candidates. Evaluate line-item extraction and latency at scale (batch runs). Produce cost projection for expected monthly volumes.
    

**Week 3 (decision & integration plan)**

- Produce POC report with metrics, recommended provider, integration approach, custom training requirements, and security/residency considerations. If managed provider chosen, produce sample API integration snippet and error-handling plan.
    

## Example acceptance criteria (for integration into Sprint-0)

- SDK/API validated end-to-end on 20 new invoices not in the benchmark set.
    
- Field-level F1 for invoice_number, date, total ≥ 0.90 on validation set.
    
- Document processing pipeline emits canonical JSON with consistent schema and logs.
    

---

# 2) RAG POC plan — embeddings, vector DB demo, retrieval + LLM pipeline

## Goal

Prove that retrieval-augmented generation (RAG) reliably improves Q&A accuracy and grounding for accounting queries (reduce hallucinations and provide source citations). Produce a lightweight demo where a user asks natural-language accounting questions and receives an answer _with anchors_ (document passages + confidence), suitable for a human reviewer.

> RAG is a widely recommended approach to reduce hallucinations by grounding model output in retrieved documents. Use RAG as the conversational layer combined with deterministic rules for journal posting. ([WIRED](https://www.wired.com/story/reduce-ai-hallucinations-with-rag?utm_source=chatgpt.com "Reduce AI Hallucinations With This Neat Software Trick"), [Eden AI](https://www.edenai.co/post/the-2025-guide-to-retrieval-augmented-generation-rag?utm_source=chatgpt.com "The 2025 Guide to Retrieval-Augmented Generation (RAG)"))

## Components & short tool recommendations

- **Embeddings**: OpenAI embeddings or a high-quality SentenceTransformer (local) depending on cost/residency. OpenAI embeddings are strong and easy to use; open-source sentence embeddings (SBERT family) are viable for on-prem. ([DEV Community](https://dev.to/simplr_sh/comparing-popular-embedding-models-choosing-the-right-one-for-your-use-case-43p1?utm_source=chatgpt.com "Comparing Popular Embedding Models: Choosing the ..."))
    
- **Vector DB**: Managed (Pinecone) for fastest start; Qdrant or Milvus for self-hosted. Pinecone simplifies operations and scales without infra overhead. ([DataCamp](https://www.datacamp.com/blog/the-top-5-vector-databases?utm_source=chatgpt.com "The 7 Best Vector Databases in 2025"), [lakefs](https://lakefs.io/blog/12-vector-databases-2023/?utm_source=chatgpt.com "Best 17 Vector Databases for 2025 [Top Picks]"))
    
- **Retriever**: semantic search (dense embeddings) + small lexical filter (match invoice ID, supplier name) for high precision.
    
- **Generator**: Hosted LLM (OpenAI / Azure OpenAI) or self-hosted Llama-family models (if on-prem required). Use the generator primarily for natural-language phrasing and for combining retrieved evidence; the factual claims must be supported by retrieved passages.
    
- **Provenance & explainability**: Always return passages + document IDs + offsets + confidence score.
    

## Demo scope (2 weeks)

- Index **1000 processed document passages** (passages = canonical JSON fields + 200-token textual chunks of invoices and notes).
    
- Implement pipeline: Document ingestion → embeddings → vector DB index → simple retrieval API → LLM prompt composition (RAG) → final answer with evidence.
    
- Build a small web UI where a user can type a question, see the answer, and expand the source passages.
    

## Step-by-step RAG POC

**Step 0 — Data & preprocessing**

- Convert canonical JSON outputs from OCR pipeline into textual passages (e.g., “Invoice #12345 — Supplier: X — Date: 2025-05-01 — Items: …”). Produce multiple chunk sizes: short passages (1–2 fields) and long passages (full invoice narrative).
    
- Add metadata to each vector: doc_id, supplier, date, invoice_number, page_no, field_type.
    

**Step 1 — Embeddings generation**

- Evaluate two embeddings approaches on a small validation set of Q/A pairs:
    
    - **OpenAI embeddings** (fast to integrate).
        
    - **SentenceTransformers (all-mpnet-base-v2 or similar)** locally.
        
- Compare retrieval quality using a small labeled set of question → expected passage IDs (precision@k). Use the better performer for the demo. ([DEV Community](https://dev.to/simplr_sh/comparing-popular-embedding-models-choosing-the-right-one-for-your-use-case-43p1?utm_source=chatgpt.com "Comparing Popular Embedding Models: Choosing the ..."))
    

**Step 2 — Index into vector DB**

- For quick start use **Pinecone** (hosted) or **Qdrant** for local. Index passage embeddings with metadata. Measure retrieval latency (P95) and precision@1/3/5. ([DataCamp](https://www.datacamp.com/blog/the-top-5-vector-databases?utm_source=chatgpt.com "The 7 Best Vector Databases in 2025"))
    

**Step 3 — Retriever + reranker**

- Retriever: nearest neighbor (ANN) to get top-k (k=10).
    
- Reranker (optional for higher precision): small cross-encoder (if resources available) or simple relevance scoring by metadata filters (date range, supplier) before feeding into LLM.
    

**Step 4 — Prompt & generator**

- Compose prompt template that **(a)** lists top retrieved passages with metadata, **(b)** instructs LLM to _only_ use those passages to answer, and **(c)** requires the LLM to produce citations (passage IDs + snippet). Example pseudo-prompt:
    
    ```
    You are an accounting assistant. Use only the following passages to answer the question.
    Passages:
    [1] DocID=inv-123 (Supplier: Acme) — "Total: 12,345 AZN ... "
    [2] DocID=inv-456 (Supplier: Beta) — ...
    Question: "What were advertising expenses last quarter?"
    Answer:  - Provide the value, reasoning, and cite passages used (IDs).
    ```
    
- Use a conservative temperature (0–0.3) to reduce creativity.
    

**Step 5 — Output & UI**

- Show final answer + list of used passages and confidence score. Provide a button: **Create Draft Journal** (only enabled after human review).
    

## Evaluation metrics

- **Precision@1/3/5**: proportion of queries whose top retrieved passage contains the ground-truth answer.
    
- **Answer accuracy**: fraction of answers that match numeric ground-truth (where applicable).
    
- **Hallucination rate**: fraction of answers that include unsupported claims (should be near zero with proper grounding). ([WIRED](https://www.wired.com/story/reduce-ai-hallucinations-with-rag?utm_source=chatgpt.com "Reduce AI Hallucinations With This Neat Software Trick"))
    
- **Latency**: end-to-end query response latency (target: <2s for retrieval + <2s for LLM latency depending on model).
    
- **User confidence / NPS**: qualitative feedback from accountants in pilot.
    

## Minimal demo acceptance criteria

- For a curated set of 50 accounting Q/A queries, **precision@3 ≥ 0.85** and **answer accuracy ≥ 0.85**.
    
- All answers include at least one passage citation.
    
- Human reviewer can make a final decision to post a journal entry within 30s of reading the answer.
    

## Example pseudocode (Python-like) — embedding + retrieve + prompt

```
# PSEUDO: not runnable, for engineering handoff
passages = get_passages_for_doc(doc_json)   # precomputed
emb = embed_texts(passages, method="openai")  # or sentence-transformer
vector_db.upsert(ids, emb, metadata=meta)

# Query time
q_emb = embed_text(query, method="openai")
results = vector_db.query(q_emb, top_k=10, filter={"supplier": "Acme"})
# build prompt
prompt = format_prompt(query, results)  # include passages + instructions
answer = llm.generate(prompt, temperature=0.0)
return { "answer": answer.text, "sources": results }
```

---

# 3) Sprint-0 backlog — fully detailed (deliverables, user stories, tasks, owners, estimates)

**Sprint-0 duration**: 2–3 weeks (recommended). Objective: remove key unknowns, deliver POC artifacts (OCR benchmark dataset, RAG sample index), and produce a prioritized backlog for Sprint-1.

> Core outcomes by end of Sprint-0:
> 
> 1. Data inventory & 150–200 labeled invoice samples (canonical JSON).
>     
> 2. OCR benchmark results for 2–3 providers on 50-sample quick set.
>     
> 3. RAG mini-demo indexing 100–200 passages with retrieval + LLM Q/A demo.
>     
> 4. Technical decision document (OCR provider + vector DB choice + hosting/residency).
>     
> 5. Sprint-1 plan and prioritized backlog.
>     

---

## Sprint-0 backlog (user stories + tasks + acceptance criteria + owners & estimates)

### Story 0.0 — Project kickoff & access

- **User story**: As Project Lead, I want the team to have access to required systems and stakeholders so the team can begin POCs.
    
- **Tasks**
    
    - A0: Kickoff meeting with SME, IT, legal (1.5h). Owner: Project Lead. (0.5 day)
        
    - A1: Obtain ERP read-only access or sample exports; define data-sharing agreement. Owner: IT/SME. (2 days)
        
    - A2: Identify document sources & legal review for sending to third-party OCR (data residency/GDPR check). Owner: Security/Compliance. (2 days)
        
- **Acceptance criteria**
    
    - Access confirmed or a path for sanitized sample export established.
        
    - Legal sign-off or approved plan for anonymized testing.
        

**Estimate:** 4 workdays (concurrent tasks).

---

### Story 0.1 — Data inventory & sampling

- **User story**: As Data Engineer, I want a labeled sample dataset of invoices, receipts and negatives so POCs can be run on representative data.
    
- **Tasks**
    
    - B0: Define canonical schema JSON (fields + types + normalization rules). Owner: Data Translator + Accounting SME. (1 day)
        
    - B1: Collect 150–200 sample documents and assign IDs. Owner: Data Engineer + SME. (3 days)
        
    - B2: Label / validate ground truth for 150 docs. Use spreadsheet with JSON exports. Owner: SME (supported by Data Engineer for tooling). (5 days; SME effort can be part-time)
        
    - B3: Create one sanitized subset for external managed services. Owner: Data Engineer. (1 day)
        
- **Acceptance criteria**
    
    - Canonical schema document stored in repo.
        
    - 150 labeled docs in canonical JSON with SME sign-off on 80% sample.
        

**Estimate:** 7 working days (overlapping with other tasks).

---

### Story 0.2 — OCR quick benchmark (50-doc quick test)

- **User story**: As ML Engineer, I want a quick benchmark comparing 2–3 OCR providers on a 50-document sample, so we can pick top candidates for full benchmark.
    
- **Tasks**
    
    - C0: Implement small harness that posts docs to Azure Form Recognizer, Google Document AI, AWS Textract, and Tesseract baseline; map outputs to canonical schema. Owner: ML Engineer. (3 days)
        
    - C1: Compute metrics (precision/recall/F1 per field), and generate per-document error reports. Owner: ML Engineer + Data Engineer. (2 days)
        
    - C2: Produce short POC report with recommendation for full benchmark. Owner: ML Engineer. (1 day)
        
- **Acceptance criteria**
    
    - Harness runs on 50 samples, metrics computed, top-2 candidates identified.
        
    - POC report with recommended provider for deeper benchmark delivered.
        

**Estimate:** 6 working days.

**Notes:** see OCR benchmark plan above for fields & metrics. ([unstract.com](https://unstract.com/blog/best-pdf-ocr-software/?utm_source=chatgpt.com "Best OCR Software in 2025 | PDF OCR Tool Comparison ..."))

---

### Story 0.3 — RAG mini-demo (index 100 passages)

- **User story**: As ML Engineer, I want a working RAG pipeline (embeddings → vector DB → LLM) so we can demonstrate Q/A with sourced answers.
    
- **Tasks**
    
    - D0: Convert 100 canonical JSON docs into passages & create metadata schema. Owner: Data Engineer. (1 day)
        
    - D1: Generate embeddings (OpenAI or local SBERT) and index into chosen vector DB (Pinecone trial or Qdrant). Owner: ML Engineer. (1 day)
        
    - D2: Implement a simple retriever + prompt composer and connect to a hosted LLM for answers. Owner: ML Engineer. (2 days)
        
    - D3: Build a minimal web UI (React) to issue queries and display answers + sources. Owner: Frontend Dev (part-time). (2 days)
        
    - D4: Evaluate retrieval precision on 20 curated queries; produce demo report. Owner: ML Engineer. (1 day)
        
- **Acceptance criteria**
    
    - Demo can answer 20 curated accounting questions with sources; precision@3 ≥ 0.80 on demo queries.
        
    - UI displays answer + source passages + option to create draft journal (disabled until human approves).
        

**Estimate:** 6 working days (parallelize embeddings + UI).

**Notes:** For fast start use managed Pinecone to avoid infra overhead. ([DataCamp](https://www.datacamp.com/blog/the-top-5-vector-databases?utm_source=chatgpt.com "The 7 Best Vector Databases in 2025"))

---

### Story 0.4 — Security, compliance & legal checklist

- **User story**: As Security/Compliance, I need to verify data residency and encryption requirements for candidate cloud services so we operate within regulations.
    
- **Tasks**
    
    - E0: Create checklist: GDPR, local tax authority constraints, data residency, encryption at rest and in transit. Owner: Compliance expert. (1 day)
        
    - E1: Confirm each candidate OCR provider and vector DB has required compliance or propose mitigations (e.g., anonymize docs, on-prem alternative). Owner: Compliance + DevOps. (2 days)
        
- **Acceptance criteria**
    
    - Compliance checklist signed by legal and recommended provider list annotated with allowed/residual risks.
        

**Estimate:** 3 working days.

---

### Story 0.5 — Dev environment & CI scaffolding

- **User story**: As Backend Dev / MLOps engineer, I want basic repo layout, Docker images, and CI pipeline to ensure reproducible builds for demos.
    
- **Tasks**
    
    - F0: Create mono-repo skeleton: services/ocr-harness, services/rag, web-ui, infra (IaC). Owner: Backend Dev. (2 days)
        
    - F1: Add GitHub Actions sample workflow: run tests, build Docker images. Owner: DevOps/MLOps. (2 days)
        
    - F2: Provision dev environment (small cloud account projects, Pinecone trial, OpenAI keys) with secrets stored in Vault. Owner: MLOps. (1 day)
        
- **Acceptance criteria**
    
    - Repo skeleton with sample CI runs; dev can run whole demo locally with documented steps.
        

**Estimate:** 5 working days (some tasks parallel).

---

### Story 0.6 — Decision & roadmap deliverable

- **User story**: As Product Owner, I want a decision document that summarizes POC outcomes, recommended stack, and Sprint-1 backlog so we can start development with minimal risk.
    
- **Tasks**
    
    - G0: Collate OCR benchmark + RAG demo results. Owner: ML Engineer + Data Engineer. (1 day)
        
    - G1: Produce recommendations: (OCR vendor choice / custom retrain needs), vector DB choice, LLM provider choice, hosting/residency. Owner: Project Lead. (1 day)
        
    - G2: Produce Sprint-1 backlog and draft 6-month roadmap. Owner: Project Lead + Data Translator. (1 day)
        
- **Acceptance criteria**
    
    - Decision doc signed by Product Owner and SME; Sprint-1 backlog accepted.
        

**Estimate:** 3 working days.

---

## Sprint-0 total estimate & staffing (summary)

- **Total calendar**: 2–3 calendar weeks with the team working in parallel. Concrete full-time-equivalent (FTE) breakdown (typical minimal setup):
    
    - Project Lead / Data Translator (part-time 20%) — oversight, coordinates legal/SME.
        
    - Accounting SME (part-time) — labeling and validation (20–40%).
        
    - Data Engineer (full-time) — dataset, ingestion, metadata.
        
    - ML Engineer (full-time) — OCR harness, embeddings, RAG demo.
        
    - Backend Dev / MLOps (full-time or 0.5 FTE) — repo, CI, infrastructure.
        
    - Frontend Dev (part-time 25%) — demo UI.
        
    - Security/Compliance (part-time) — 0.2 FTE for checklists.
        

**Deliverables by Sprint-0 end**

- Labeled dataset (150–200 canonical JSON docs) and sanitized subset.
    
- OCR quick benchmark report (50 docs) and recommendation for full benchmark.
    
- RAG demo with 100 passage index, UI, demo recording.
    
- Decision document + Sprint-1 backlog.
    

---

# Risks & mitigations during Sprint-0 (concise)

1. **Insufficient labeled samples** — Mitigate: collect early, use minimal manual labeling and semi-supervised mapping for repetitive fields.
    
2. **Cloud/legal blocking** — Mitigate: sanitize/anonymize samples for managed services, evaluate on-prem alternative (Tesseract + SBERT + Qdrant).
    
3. **Latency surprises** — Mitigate: measure at scale in POC and add caching for heavy queries.
    

---

# Quick reference recommendations (one-line)

- **OCR**: start with **Azure Form Recognizer** or **Google Document AI** for fastest, most accurate invoice parsing; fall back to on-prem Tesseract only if data residency prohibits cloud. ([unstract.com](https://unstract.com/blog/best-pdf-ocr-software/?utm_source=chatgpt.com "Best OCR Software in 2025 | PDF OCR Tool Comparison ..."), [skillup.ccccloud.com](https://skillup.ccccloud.com/2025/06/17/ai-document-analysis-tools-comparing-aws-textract-vs-azure-form-recognizer/?utm_source=chatgpt.com "Comparing AWS Textract vs Azure Form Recognizer – SkillUp"))
    
- **Vector DB**: use **Pinecone** for managed ease or **Qdrant** if you prefer self-hosted. ([DataCamp](https://www.datacamp.com/blog/the-top-5-vector-databases?utm_source=chatgpt.com "The 7 Best Vector Databases in 2025"), [lakefs](https://lakefs.io/blog/12-vector-databases-2023/?utm_source=chatgpt.com "Best 17 Vector Databases for 2025 [Top Picks]"))
    
- **Embeddings**: begin with **OpenAI embeddings** for simplicity; benchmark SBERT for a lower-cost on-prem option. ([DEV Community](https://dev.to/simplr_sh/comparing-popular-embedding-models-choosing-the-right-one-for-your-use-case-43p1?utm_source=chatgpt.com "Comparing Popular Embedding Models: Choosing the ..."))
    
- **RAG**: use retriever + generator with enforced citation in prompt and human-in-loop for journal posting to avoid financial risks. ([WIRED](https://www.wired.com/story/reduce-ai-hallucinations-with-rag?utm_source=chatgpt.com "Reduce AI Hallucinations With This Neat Software Trick"))