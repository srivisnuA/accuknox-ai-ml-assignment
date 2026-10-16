# Submission notes — personalize before sending

The recruiter explicitly warns against copied AI responses. Use these notes to prepare, verify claims about your own work, and rewrite answers in your own voice. Do not claim contributions you cannot explain.

## Assignment 1 — Q4: most complex Python code

Suggested link: https://github.com/srivisnuA/FaceFare

Repository structure shows a Flask/Socket.IO backend, camera/face recognition modules, trip and fare services, SQLite-backed wallet handling, passenger enrollment and tests.

Draft to adapt:
“My most complex Python implementation is FaceFare, a face-recognition-based public-transport fare collection prototype. It combines camera processing, face-recognition integration, trip/session state, fare calculation, wallet operations, SQLite persistence, and a Flask/Socket.IO dashboard. The implementation separates major responsibilities into modules and adds validation around passenger enrollment and wallet updates. It remains a prototype; before production I would further strengthen integration coverage and recognition stability.”

## Assignment 1 — Q5: most complex database code

Suggested links:
- https://github.com/srivisnuA/FaceFare/tree/main/database
- https://github.com/srivisnuA/FaceFare/blob/main/database/db.py
- https://github.com/srivisnuA/FaceFare/blob/main/database/models.py
- https://github.com/srivisnuA/FaceFare/blob/main/services/wallet.py

Draft to adapt:
“My most substantial database implementation is the SQLite layer in FaceFare. It initializes the schema, uses a primary key for passenger IDs, validates wallet values, uses parameterized queries, closes connections reliably, and performs wallet adjustments in a transaction. The wallet service uses the database layer so the in-memory dashboard state changes only after a successful persisted update. This is a small SQLite application rather than a large database system, but it demonstrates practical persistence and transaction handling.”

Interview detail: `BEGIN IMMEDIATE` obtains a reserved write lock early. A conditional update can prevent a balance becoming negative. A transaction should commit only after successful operations and roll back on failure.

## Assignment 2 — Q1: skill self-rating

Choose ratings honestly. A = can code independently; B = can code under supervision; C = little/no understanding. Use personal evidence for each:

| Area | Your rating | Evidence to be ready to discuss |
|---|---|---|
| LLM | [A/B/C] | API integration, prompting, RAG, evaluation or limitations you personally implemented/studied |
| Deep Learning | [A/B/C] | PyTorch/TensorFlow model training, inference and evaluation in ChestXpert |
| AI | [A/B/C] | AI methods you can explain and implement independently |
| ML | [A/B/C] | Preprocessing, model selection, metrics and error analysis |

Do not rate yourself A only because you can explain theory.

## Assignment 2 — Q2: high-level LLM chatbot architecture

Use these points to create your own explanation:
1. Client/UI accepts questions and displays answers.
2. Application/API authenticates users, validates inputs, manages sessions and rate limits.
3. Orchestration builds prompts from system instructions, recent history and relevant context; it decides whether tools are needed.
4. Optional RAG pipeline chunks trusted documents, creates embeddings, retrieves relevant passages and supplies them to the model.
5. LLM generates a response using the prompt and supplied context.
6. Optional tools call controlled APIs/business functions; validate arguments and require confirmation for consequential actions.
7. Safety/privacy include access controls, prompt-injection defenses for retrieved material, secret management and data retention.
8. Storage persists approved conversation history and metadata.
9. Observability tracks latency, errors, cost, retrieval quality, groundedness and feedback.

Flow: user message → authenticate/validate → retrieve context when relevant → build prompt → model/tool execution → validate response → return answer → log minimal telemetry.

Example assumption: internal company-document Q&A with permission-restricted documents and citations. Retrieved content must not expose documents the user is not permitted to access.

## Assignment 2 — Q3: vector databases

Explain in your own words:
- An embedding is a numeric vector representing semantic features of text, images or other content.
- A vector database stores vectors and metadata and retrieves nearest items using similarity/distance measures such as cosine similarity, dot product or Euclidean distance.
- With RAG, documents are split into chunks, embedded and indexed; query embeddings retrieve relevant chunks that become context for an LLM.
- Similarity is not proof of truth. Use access controls, metadata filters, source references and evaluation.

Hypothetical use case: an internal support chatbot indexes 100,000 policy/troubleshooting chunks and must filter by team permissions and cite sources.

A reasonable choice is PostgreSQL with pgvector if the organization already runs PostgreSQL and needs relational metadata and vector search in one system. This can reduce operational complexity and support combining metadata filters with similarity search. At higher search scale/throughput, compare purpose-built options such as Qdrant or Pinecone using real benchmarks for recall, latency, filtering, cost and operations. No database is universally best.

Discuss corpus size, query volume, latency/recall, metadata filters, tenant isolation, updates/deletes, hosting, team familiarity, backups and cost.

## Before submitting

- Rewrite the frameworks in your own voice.
- Confirm which FaceFare functions you personally implemented.
- Select real self-ratings for all four areas.
- Attach your latest resume.
- Run the scripts/tests and be prepared to explain choices.
