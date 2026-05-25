# rag-assistant-project

##Architecture Diagram
┌─────────────────────────────────────────────────────────────────┐
│                        STARTUP (Indexing)                       │
│                                                                 │
│  docs.json ──► Chunker ──► Embedding Model ──► Vector Store     │
│   (10 docs)   (≈300-500      (all-MiniLM-L6-v2     (in-memory  │
│               token chunks)   or OpenAI API)        cosine sim) │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    RUNTIME (Per Request)                        │
│                                                                 │
│  User Query                                                     │
│      │                                                          │
│      ▼                                                          │
│  Embed Query ──► Cosine Similarity Search ──► Top-K Chunks      │
│  (same model)    (vs all indexed vectors)    (K=3, threshold)   │
│                                                      │          │
│                              Conversation History ◄──┤          │
│                                                      │          │
│                              Build RAG Prompt ◄──────┤          │
│                                                      │          │
│                              LLM API Call ◄──────────┤          │
│                                 (Gemini)             │          │
│                                                      │          │
│                                                      │          │
│                              Response ──────────────►│          │
│                              + save to history       │          │
│                                                      ▼          │
│                                              JSON Response      │
└─────────────────────────────────────────────────────────────────┘

##Project Structure
project/
├── app/
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   ├── routes/
│   │   └── chat.py             # POST /api/chat, GET /health
│   ├── services/
│   │   ├── embeddings.py       # Embedding generation (ST or OpenAI)
│   │   ├── retrieval.py        # Query embedding + similarity search
│   │   ├── llm.py              # LLM provider integrations
│   │   ├── conversation.py     # Session history management
│   │   └── rag.py              # RAG orchestrator
|   |   └── storage.py          # Storage 
│   ├── vectorstore/
│   │   └── store.py            # In-memory vector store (cosine sim)
│   ├── prompts/
│   │   └── templates.py        # Prompt templates
│   ├── utils/
│   │   ├── chunker.py          # Document chunking logic
│   │   └── logger.py           # Centralised logging
│   └── main.py                 # FastAPI app + startup indexing
│
├── frontend/
│   ├── index.html              # Chat UI
│   ├── styles.css              # Dark editorial styling
│   └── app.js                  # Frontend logic
│
├── docs.json                   # 10-document knowledge base
├── requirements.txt
├── .env.example
└── README.md

##Setup Instructions
1. Clone/download the project
git clone https://github.com/<Rakshitha0713>/rag-assistant.git
cd rag-assistant

2. Create a virtual environment
python -m venv venv
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Configure environment variables
cp .env .env
Open .env and set:
Variable                                                        Description
LLM_PROVIDER                                          claude / openai / gemini / mistral
CLAUDE_API_KEY                                      Your Anthropic API key (if using Claude)
OPENAI_API_KEY                                       Your OpenAI API key (if using OpenAI)
GEMINI_API_KEY                                       Your Google API key (if using Gemini)
MISTRAL_API_KEY                                     Your Mistral API key (if using Mistral)
EMBEDDING_PROVIDER                                   sentence_transformers (free) or openai
SIMILARITY_THRESHOLD                                 Minimum cosine score (default: 0.30)
TOP_K                                               Chunks to retrieve per query (default: 3)
Using Gemini:
pip install google-generativeai

5. Run the server
uvicorn app.main:app --reload --port 8001

6. Open the frontend
Visit http://localhost:8001 in your browser.

##RAG Workflow Explanation
Indexing (startup): All documents in docs.json are loaded, split into overlapping chunks of ~300-500 tokens, converted to vector embeddings, and stored in memory.
Query: When a user submits a message, the same embedding model converts it to a vector.
Similarity search: Cosine similarity is computed between the query vector and every stored document vector. The top-K results above the threshold are retrieved.
Prompt construction: Retrieved chunks are formatted as context, combined with conversation history and the user's question, and passed to the LLM.
Grounded response: The LLM is instructed to answer only from the provided context, preventing hallucination. If no chunks pass the threshold, a fallback message is returned.

##Embedding Strategy
Model: all-MiniLM-L6-v2 (sentence-transformers) — 384-dimensional dense vectors, trained for semantic similarity.
Normalization: L2-normalized embeddings, so cosine similarity equals dot product.
Batching: All document chunks are embedded in a single batch at startup for efficiency.

##Similarity Search Explanation
Cosine Similarity measures the angle between two vectors:
similarity = (A · B) / (||A|| × ||B||)
Score of 1.0 = identical direction (very similar meaning)
Score of 0.0 = orthogonal (unrelated)
Score below threshold → fallback response

##Prompt Design Reasoning
The prompt follows a strict structure:
  SYSTEM: You are a helpful assistant. Answer ONLY from the context.
  USER:
  Context: <retrieved chunks with source labels>
  Conversation History: <last 3-5 exchanges>
  Question: <current user message>
  Answer:
    System prompt enforces grounding and prevents hallucination.
    Context first so the LLM attends to it most strongly.
    History enables follow-up questions.
    Low temperature (0.2) produces consistent, factual answers.
