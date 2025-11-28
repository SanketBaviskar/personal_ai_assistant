# Personal AI Knowledge Assistant

A secure, multi-source Personal AI Assistant that unifies your data from Notion, Jira, and Email into a private knowledge base. It uses Retrieval-Augmented Generation (RAG) to provide grounded, context-aware answers.

## Architecture Overview

The system is built on a micro-service architecture (monolith deployment) using FastAPI. It strictly enforces Access Control Lists (ACLs) at every layer to ensure data isolation between users.

### Key Components

1.  **Connectors**: Fetch data from external sources (Notion, Jira, Email).
2.  **RAG Pipeline**: Cleans, chunks, and indexes data into a Vector Database.
3.  **Vector DB**: Stores embeddings with strict metadata (user_id, source).
4.  **Retriever**: Semantically searches for relevant context.
5.  **Memory Service**: Manages conversation history.
6.  **LLM Generator**: Synthesizes answers using retrieved context and history.

---

## Workflows & Service Interactions

### 1. Data Ingestion Pipeline (Sync)

This workflow runs periodically (via Scheduler) or manually to keep the knowledge base up-to-date.

```mermaid
sequenceDiagram
    participant Scheduler as APScheduler
    participant Sync as SyncService
    participant Conn as Connectors (Notion/Jira)
    participant RAG as RAGPipeline
    participant Chunker as ChunkerService
    participant VDB as VectorDB (Chroma)

    Scheduler->>Sync: Trigger sync_user_data(user_id)
    activate Sync

    loop For each Provider
        Sync->>Conn: fetch_data(credentials)
        activate Conn
        Conn-->>Sync: Return Raw Documents
        deactivate Conn

        loop For each Document
            Sync->>RAG: process_document(text, metadata)
            activate RAG
            RAG->>Chunker: chunk_text(text)
            Chunker-->>RAG: [Chunk 1, Chunk 2, ...]

            loop For each Chunk
                RAG->>VDB: index_document(chunk, user_id)
                note right of VDB: Enforces ACL (user_id)
            end
            deactivate RAG
        end
    end
    deactivate Sync
```

**Interaction Details:**

1.  **Scheduler** triggers the `SyncService` for a specific user.
2.  **SyncService** retrieves encrypted credentials and calls the appropriate **Connector**.
3.  **Connector** fetches raw data (pages, tickets, emails) and normalizes it.
4.  **RAGPipeline** takes the raw text, sanitizes it (PII masking), and passes it to the **ChunkerService**.
5.  **ChunkerService** splits the text into semantically meaningful chunks (recursive character split).
6.  **VectorDB** indexes each chunk, tagging it with `user_id` and `source_url` to ensure security and traceability.

---

### 2. Chat & Retrieval Pipeline (Query)

This workflow handles user questions, retrieving context and generating an answer.

```mermaid
sequenceDiagram
    actor User
    participant API as Chat Endpoint
    participant Retriever as RetrieverService
    participant VDB as VectorDB
    participant Memory as MemoryService
    participant LLM as LLMGenerator

    User->>API: POST /chat (query)
    activate API

    par Retrieve Context
        API->>Retriever: retrieve_context(user_id, query)
        activate Retriever
        Retriever->>VDB: query(embedding, filter=user_id)
        VDB-->>Retriever: Relevant Chunks
        Retriever-->>API: Context Docs
        deactivate Retriever
    and Retrieve History
        API->>Memory: get_history(conversation_id)
        Memory-->>API: Chat History
    end

    API->>LLM: generate_response(query, context, history)
    activate LLM
    note right of LLM: System Prompt enforces<br/>"Answer ONLY using Context"
    LLM-->>API: Generated Answer
    deactivate LLM

    API->>Memory: save_exchange(query, answer)
    API-->>User: Response (Answer + Citations)
    deactivate API
```

**Interaction Details:**

1.  **User** sends a query via the API.
2.  **Chat Endpoint** orchestrates the flow.
3.  **Retriever** converts the query to a vector and searches the **VectorDB**, strictly filtering by `user_id`.
4.  **MemoryService** fetches the recent conversation history to allow follow-up questions.
5.  **LLMGenerator** constructs a prompt containing the System Instruction, History, Retrieved Context, and the User Query. It sends this to the LLM (Gemini).
6.  **LLM** generates a grounded response.
7.  **MemoryService** saves the new user query and assistant response.
8.  **API** returns the answer along with the source citations (URLs) to the user.

---

## Setup & Deployment

### Prerequisites

-   Python 3.10+
-   `GEMINI_API_KEY` (for LLM)
-   `SECRET_KEY` (for Auth)

### Installation

```bash
pip install -r requirements.txt
```

### Running the App

```bash
uvicorn app.main:app --reload
```

### API Documentation

Visit `http://localhost:8000/docs` for the interactive Swagger UI.
