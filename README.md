<div align="center">

# RAG API

**A Retrieval-Augmented Generation backend built with FastAPI.**

Upload documents, index them into a vector database, and get context-aware answers from an LLM through an authenticated REST API.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688)](https://fastapi.tiangolo.com/)

[Getting Started](#getting-started) · [API Reference](#api-reference) · [Architecture](#architecture) · [Known Limitations](#known-limitations)

</div>

---

## Overview

RAG API is a self-hostable backend for building question-answering systems over your own documents. It handles file ingestion, chunking, embedding, vector indexing, and LLM-based answer generation behind a REST API.

Users register and log in; every project is owned by the account that created it, and one user cannot read or modify another user's projects.

**Highlights:**

- 🔐 JWT authentication with per-user project ownership
- 📄 PDF and plain-text ingestion with configurable chunking
- 🔎 Semantic search and retrieval-augmented answer generation
- 🔌 Pluggable LLM and vector-database providers via a factory pattern (OpenAI, Cohere, Qdrant)
- 🌍 Multi-language prompt templates

> **This project is under active development.** Authentication and per-user data isolation are implemented; several other production hardening steps are not yet in place. See [Known Limitations](#known-limitations) before deploying this anywhere publicly reachable.

---

## Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Authentication](#authentication)
- [API Reference](#api-reference)
- [Known Limitations](#known-limitations)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Architecture

### Ingestion pipeline

```
Upload (PDF / TXT)
      │
      ▼
  Chunking  ──────────►  LangChain text splitter
      │
      ▼
  Embedding ──────────►  OpenAI / Cohere embedding model
      │
      ▼
  Indexing  ──────────►  Qdrant vector store
```

### Query pipeline

```
User question
      │
      ▼
  Embed query ─────────►  Embedding model
      │
      ▼
  Vector search ───────►  Qdrant  ──►  relevant chunks
      │
      ▼
  Prompt augmentation ─►  Generative model (GPT / Command R)
      │
      ▼
  Answer returned to user
```

### Auth & ownership

```
POST /auth/register or /auth/login  ──►  { access_token }

Every subsequent request:
  Authorization: Bearer <token>
      │
      ▼
  Token decoded → user_id
      │
      ▼
  Project lookup scoped to (project_id, user_id)
```

A `project_id` alone does not grant access — every project is bound to the account that created it, and requests without a valid token are rejected.

---

## Tech Stack

| Layer            | Technology                             |
| ---------------- | -------------------------------------- |
| API framework    | FastAPI                                |
| Authentication   | JWT (`python-jose`) + `bcrypt` hashing |
| LLM providers    | OpenAI, Cohere (pluggable)             |
| Vector database  | Qdrant                                 |
| Application DB   | MongoDB                                |
| Document parsing | LangChain                              |
| Configuration    | Pydantic Settings                      |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- An API key from at least one supported LLM provider (OpenAI and/or Cohere)

### 1. Clone and configure

```bash
git clone https://github.com/ahmedwaleed01/RAG.git
cd RAG
cp .env.example .env
```

Edit `.env` with your own values (see [Configuration](#configuration)).

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r src/requirements.txt
```

### 3. Start MongoDB

```bash
cd docker
docker-compose up -d
cd ..
```

### 4. Run the API

```bash
cd src
uvicorn main:app --reload
```

The API is now live at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

---

## Configuration

All configuration is provided via environment variables (`.env` locally). Key settings:

| Variable                            | Description                                                  | Example                          |
| ----------------------------------- | ------------------------------------------------------------ | -------------------------------- |
| `EMBEDDING_BACKEND`                 | Embedding provider: `openai` or `cohere`                     | `openai`                         |
| `GENERATION_BACKEND`                | Generation provider: `openai` or `cohere`                    | `openai`                         |
| `OPENAI_API_KEY` / `COHERE_API_KEY` | Provider API key                                             | —                                |
| `GENERATION_MODEL_ID`               | Model used for answer generation                             | `gpt-3.5-turbo`                  |
| `EMBEDDING_MODEL_ID`                | Model used for embeddings                                    | `text-embedding-3-small`         |
| `VECTOR_DB_BACKEND`                 | Vector store backend                                         | `qdrant`                         |
| `MONGODB_URL`                       | MongoDB connection string                                    | `mongodb://user:pass@host:27017` |
| `JWT_SECRET`                        | Secret used to sign access tokens — set a long, random value | —                                |
| `FILE_MAX_SIZE`                     | Max upload size in bytes                                     | `10485760` (10 MB)               |
| `DEFAULT_LANGUAGE`                  | Default prompt language                                      | `en`                             |

See [`.env.example`](./.env.example) for the complete list.

> `.env` is intended for local development. Set `JWT_SECRET` to a long random value — never reuse a default or example value in any deployment others can reach.

---

## Authentication

Every `/data` and `/nlp` endpoint requires a bearer token.

**Register**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "your_password"}'
```

**Log in**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "your_password"}'
```

Both return:

```json
{ "access_token": "eyJhbGciOiJIUzI1NiIs..." }
```

**Authenticated request example**

```bash
curl -X POST http://localhost:8000/api/v1/nlp/index/answer/my_project \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"text": "What does this document say about refunds?"}'
```

---

## API Reference

| Method | Endpoint                                | Auth | Description                                |
| ------ | --------------------------------------- | ---- | ------------------------------------------ |
| `POST` | `/api/v1/auth/register`                 | –    | Create an account                          |
| `POST` | `/api/v1/auth/login`                    | –    | Authenticate and receive a token           |
| `POST` | `/api/v1/data/upload/{project_id}`      | ✅   | Upload a PDF or text file                  |
| `POST` | `/api/v1/data/process/{project_id}`     | ✅   | Chunk uploaded files                       |
| `POST` | `/api/v1/nlp/index/push/{project_id}`   | ✅   | Embed and index chunks                     |
| `GET`  | `/api/v1/nlp/index/info/{project_id}`   | ✅   | Get vector collection info                 |
| `POST` | `/api/v1/nlp/index/search/{project_id}` | ✅   | Semantic search over indexed chunks        |
| `POST` | `/api/v1/nlp/index/answer/{project_id}` | ✅   | Ask a question, get a RAG-generated answer |

Full interactive documentation (request/response schemas, try-it-out) is auto-generated at `/docs` (Swagger UI) and `/redoc`.

---

## Known Limitations

This project has authentication and per-user data isolation, but is **not yet hardened for a public, internet-facing deployment**. If you plan to expose this beyond local/trusted use, be aware of the following:

- **No rate limiting.** Any authenticated user can call LLM-backed endpoints (`/index/push`, `/index/answer`) without limit, which can drive up your OpenAI/Cohere costs quickly. Register/login endpoints are also unthrottled and susceptible to brute-force attempts.
- **No CORS restrictions configured.** The API does not currently restrict which browser origins may call it.
- **No path-traversal sanitization** on identifiers (e.g. `project_id`) used to build filesystem paths — a crafted identifier could potentially write outside the intended directory.
- **Secrets are managed via `.env` only** — no integration with a secrets manager or vault for production deployments.

If you deploy this somewhere reachable by untrusted users, treat the items above as required work, not optional polish — particularly rate limiting, given it directly controls your LLM spend.

---

## Project Structure

```
RAG/
├── docker/
│   └── docker-compose.yml     # MongoDB service
├── src/
│   ├── controllers/           # Business logic (data, project, NLP, base)
│   ├── models/                # Pydantic schemas & Mongo data access
│   ├── routes/                # FastAPI routers (auth, data, nlp)
│   ├── helpers/                # Config, security, dependencies
│   ├── store/                  # LLM & vector DB provider factories
│   ├── main.py                 # App entrypoint
│   └── requirements.txt
├── .env.example
└── README.md
```

---

## Roadmap

- [ ] Rate limiting on LLM-backed and auth endpoints
- [ ] CORS configuration
- [ ] Path-traversal sanitization for user-supplied identifiers
- [ ] Async LLM provider calls (remove event-loop blocking under load)
- [ ] Delete/list endpoints for projects and individual files
- [ ] Streaming answer responses (Server-Sent Events)
- [ ] Automated test suite and CI pipeline
- [ ] Dockerfile for the API service
- [ ] Structured logging and basic metrics
- [ ] Secrets manager integration for production deployments

Contributions toward any of these are welcome — see below.

---

## Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes with a clear message
4. Open a pull request describing what changed and why

Please open an issue first for larger changes so they can be discussed before you invest the time.

<div align="center">

Built by [Ahmed Waleed](https://github.com/ahmedwaleed01)

</div>
