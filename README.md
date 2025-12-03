# Personal AI Knowledge Assistant

A secure, multi-source Personal AI Assistant that unifies your data from Notion, Jira, and Email into a private knowledge base. It uses Retrieval-Augmented Generation (RAG) to provide grounded, context-aware answers.

## System Architecture

The system follows a modern **Split Deployment Architecture**, separating the frontend and backend for scalability and performance.

```mermaid
graph TD
    subgraph Client ["Frontend (Vercel)"]
        UI[React + Vite UI]
        Auth_UI[Google OAuth Client]
    end

    subgraph Server ["Backend (Railway)"]
        API[FastAPI Server]
        Worker[Background Workers]
        RAG[RAG Engine]
    end

    subgraph Data ["Persistence (Supabase)"]
        DB[(PostgreSQL DB)]
        Pooler[Connection Pooler]
    end

    subgraph External ["External Services"]
        Google[Google Drive API]
        Gemini[Gemini Pro LLM]
    end

    UI -->|REST API| API
    UI -->|Auth Token| Auth_UI
    Auth_UI -.->|Verify| Google

    API -->|Read/Write| Pooler
    Pooler --> DB

    API -->|Generate| Gemini
    API -->|Ingest| Google

    Worker -->|Async Processing| RAG
```

### Key Components

1.  **Frontend (Vercel)**: A responsive React application built with Vite and TailwindCSS. It handles user interactions, file uploads, and chat visualization.
2.  **Backend (Railway)**: A stateless FastAPI service. It manages authentication, orchestrates the RAG pipeline, and communicates with the LLM.
3.  **Database (Supabase)**: A managed PostgreSQL database for storing user profiles, conversation history, and document metadata.
4.  **Vector Store**: ChromaDB (running within the backend container or separately) for storing document embeddings.
5.  **AI Engine**: Google Gemini Pro for generating grounded responses.

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

# Personal AI Knowledge Assistant

A secure, multi-source Personal AI Assistant that unifies your data from Notion, Jira, and Email into a private knowledge base. It uses Retrieval-Augmented Generation (RAG) to provide grounded, context-aware answers.

## System Architecture

The system follows a modern **Split Deployment Architecture**, separating the frontend and backend for scalability and performance.

```mermaid
graph TD
    subgraph Client ["Frontend (Vercel)"]
        UI[React + Vite UI]
        Auth_UI[Google OAuth Client]
    end

    subgraph Server ["Backend (Railway)"]
        API[FastAPI Server]
        Worker[Background Workers]
        RAG[RAG Engine]
    end

    subgraph Data ["Persistence (Supabase)"]
        DB[(PostgreSQL DB)]
        Pooler[Connection Pooler]
    end

    subgraph External ["External Services"]
        Google[Google Drive API]
        Gemini[Gemini Pro LLM]
    end

    UI -->|REST API| API
    UI -->|Auth Token| Auth_UI
    Auth_UI -.->|Verify| Google

    API -->|Read/Write| Pooler
    Pooler --> DB

    API -->|Generate| Gemini
    API -->|Ingest| Google

    Worker -->|Async Processing| RAG
```

### Key Components

1.  **Frontend (Vercel)**: A responsive React application built with Vite and TailwindCSS. It handles user interactions, file uploads, and chat visualization.
2.  **Backend (Railway)**: A stateless FastAPI service. It manages authentication, orchestrates the RAG pipeline, and communicates with the LLM.
3.  **Database (Supabase)**: A managed PostgreSQL database for storing user profiles, conversation history, and document metadata.
4.  **Vector Store**: ChromaDB (running within the backend container or separately) for storing document embeddings.
5.  **AI Engine**: Google Gemini Pro for generating grounded responses.

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

-   **Docker & Docker Compose** (for local dev)
-   **Supabase Account** (for database)
-   **Google Cloud Project** (for OAuth & Drive API)
-   **Gemini API Key**

### Local Development (Docker)

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/SanketBaviskar/personal_ai_assistant.git
    cd personal_ai_assistant
    ```

2.  **Configure Environment Variables**:

    -   Create `backend/.env` (see `backend/.env.example`)
    -   Create `frontend/.env` (see `frontend/.env.example`)

3.  **Run with Docker Compose**:
    ```bash
    docker-compose up --build
    ```
    -   Frontend: `http://localhost:5173`
    -   Backend: `http://localhost:8000`

### Production Deployment

#### 1. Database (Supabase)

-   Create a new project.
-   Use the **Session Pooler** connection string (Port 6543) for the backend.
-   Run `backend/init_cloud_db.py` to create tables.

#### 2. Backend (Railway)

-   Connect GitHub repo.
-   Set Root Directory to `/backend`.
-   Add variables: `DATABASE_URL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GEMINI_API_KEY`.

#### 3. Frontend (Vercel)

-   Connect GitHub repo.
-   Set Root Directory to `/frontend`.
-   Add variables: `VITE_API_URL` (Railway URL), `VITE_GOOGLE_CLIENT_ID`.
