# TTC Smart Chat Assistant

## Overview

This project is a multi-service AI-powered chat application focused on the Toronto Transit Commission (TTC). It combines real-time data, semantic search, and intelligent routing to provide users with transit-related information in a natural language interface.

The system is implemented using Streamlit for the frontend and integrates multiple backend services, including API calls, vector search (ChromaDB), and OpenAI function calling.

---

## Architecture

The application is divided into three services:

### 1. Service 1 — Real-Time API (TTC Arrivals)

* Uses TTC NextBus API (XML-based)
* Retrieves real-time arrival predictions using a stop ID
* Transforms raw API data into natural language summaries using an LLM
* Example:

  > “Route 53 is arriving in 7, 10, and 14 minutes. All buses are on schedule.”

**Key Decisions:**

* XML parsing handled in backend
* Output is summarized using OpenAI (not raw API response)
* Limited to top 3 arrivals for clarity

---

### 2. Service 2 — Semantic Search (RAG)

* Uses preprocessed TTC knowledge stored as `.txt` files
* Embeddings generated using OpenAI (`text-embedding-3-small`)
* Stored in **ChromaDB (persistent local storage)**
* Supports queries like:

  * Route descriptions
  * Subway line details
  * PRESTO usage
  * Policies and FAQs

**Pipeline:**

```
User Query → Embedding → ChromaDB → Top Chunks → LLM → Answer
```

**Key Decisions:**

* Used `.txt` files instead of CSV for better document structure
* Chunking: ~400 words with overlap
* Precomputed embeddings (not generated at runtime)
* Limited retrieval to top 3–5 chunks

---

### 3. Service 3 — Smart TTC Assistant (Function Calling)

* Uses OpenAI function calling to route user queries dynamically
* Decides whether to:

  * Call real-time API (Service 1)
  * Use semantic search (Service 2)
  * Respond directly

**Supported Functions:**

* `get_next_arrivals(stop_id)`
* `ask_ttc_question(question)`

**Example:**

| User Input              | Action          |
| ----------------------- | --------------- |
| “Next bus at stop 8213” | API call        |
| “Tell me about Line 1”  | Semantic search |
| “How does PRESTO work?” | Semantic search |

**Key Decisions:**

* Single-step function calling (no multi-agent orchestration)
* Original user input passed to semantic search to avoid LLM rewriting issues
* Clear separation of responsibilities between services

---

## Guardrails & Safety

The system includes input and model-level guardrails:

### Restricted Topics

The assistant will not respond to:

* Cats or dogs
* Horoscopes or zodiac signs
* Taylor Swift

### Prompt Protection

* Prevents access to system prompt
* Blocks prompt injection attempts (e.g., “ignore previous instructions”)

### Implementation

* Input-level filtering using regex
* System prompt constraints enforced at LLM level
* Tool whitelist to prevent unauthorized function calls

---

## Project Structure

```
05_src/
  assignment_chat/
    streamlit_service.py
    service1_api.py
    service2_semantic.py
    service3_router.py
    build_embeddings.py
    chroma_db/
  
  documents/
    ttc_docs/
```

---

## Embedding Process

Embeddings are generated using `build_embeddings.py`:

1. Load `.txt` documents
2. Split into chunks (400 words with overlap)
3. Generate embeddings via OpenAI
4. Store in ChromaDB with metadata

Embeddings are **precomputed** and stored in the repository.
They are not generated at runtime.

---

## Limitations

* Real-time API requires **stop ID**, not route number
* No full trip planning (no origin-destination routing)
* ChromaDB is local (not distributed or scalable)
* Semantic search relies on curated dataset quality

Part of the assignment used Google search and external resources to build the solution.

---


---

## Summary

This project demonstrates:

* API integration with real-time data
* Retrieval-Augmented Generation (RAG)
* Function calling for intelligent routing
* Guardrails for safe AI behavior

It is designed to be modular, explainable, and aligned with production-style AI system patterns.


