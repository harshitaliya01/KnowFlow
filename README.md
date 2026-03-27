# 📄 Document Q&A System with RAG

A production‑ready FastAPI application that allows users to upload PDF documents, process them into vector embeddings, and ask questions using a retrieval‑augmented generation (RAG) pipeline.

## ✨ Features

- User authentication (JWT, Argon2 hashing)
- Upload PDF documents (≤5 MB) to Supabase storage
- Asynchronous document processing (chunking, vectorisation) with Celery + Redis
- Vector search using Qdrant
- LLM‑based Q&A using an OpenAI‑compatible endpoint
- Rate limiting with SlowAPI
- Structured logging and global error handling
- Docker Compose for easy deployment

## 🧱 Tech Stack

- **Backend**: FastAPI, SQLAlchemy (async), asyncpg
- **Task Queue**: Celery, Redis
- **Vector Database**: Qdrant
- **File Storage**: Supabase (S3‑compatible)
- **Embeddings & LLM**: LangChain, OpenAI‑compatible API
- **Authentication**: JWT (python‑jose), Argon2
- **Containerization**: Docker, Docker Compose

## 📋 Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional)
- PostgreSQL database (Supabase or local)
- Qdrant instance (can run via Docker)
- Redis (can run via Docker)

## 🔧 Environment Variables

Create a `.env` file in the root with the following variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async URL (e.g., `postgresql+asyncpg://user:pass@host/db`) |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (for storage operations) |
| `QDRANT_URL` | Qdrant server URL (e.g., `http://localhost:6333`) |
| `COLLECTION_NAME` | Qdrant collection name (default: `DOCUMENTS`) |
| `REDIS_URL` | Redis URL (e.g., `redis://redis:6379/0`) |
| `OPENAI_API_KEY` | API key for the LLM (if required by your provider) |

## 🚀 Getting Started

### Using Docker Compose (recommended)

1. Clone the repository.
2. Create a `.env` file with the required variables.
3. Run:
   ```bash
   docker-compose up --build
