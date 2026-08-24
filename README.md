# RAG API Backend

This project is a Python-based backend for a **Retrieval-Augmented Generation (RAG)** system, built with FastAPI. It provides an end-to-end solution for building a question-answering service over your own documents. You can upload files, which are then processed, indexed into a vector database, and used by a Large Language Model (LLM) to generate context-aware answers to user queries.

---

## Core Features

- **Project-Based Workspaces:** Isolates documents and indexes using a `project_id`.
- **File Upload:** Supports `.pdf` and `.txt` file uploads.
- **Document Processing:** Splits documents into smaller, overlapping text chunks using `langchain`.
- **Vector Indexing:** Converts text chunks into embeddings and stores them in a vector database for semantic search.
- **Answer Generation:** Uses retrieved documents to generate answers with an LLM.
- **Pluggable Architecture:** Easily switch between different LLM providers (OpenAI, Cohere) and Vector Databases (Qdrant) through a factory pattern.
- **Localization:** Supports multi-language prompts for system instructions.

## Architecture

### Data Ingestion Flow

```
File Upload (PDF, TXT) -> [FastAPI Backend]
                             |
1. Chunking -----------------> (Text Chunks via LangChain)
                             |
2. Embedding ----------------> [Embedding Model (OpenAI/Cohere)] -> (Chunk Vectors)
                             |
3. Indexing -----------------> [Vector DB (Qdrant)]
```

### Query & Response Flow

```
User Query -> [FastAPI Backend]
                    |
1. Embedding -------> [Embedding Model] -> (Query Vector)
                    |
2. Search ----------> [Vector DB (Qdrant)] -> (Retrieved Documents)
                    |
3. Augment & Gen --> [Generative Model (GPT/Command R)] -> (Augmented Prompt)
                    |
Response <---------- [FastAPI Backend]
```

## Tech Stack

| Component        | Technology                 |
| ---------------- | -------------------------- |
| Web Framework    | FastAPI                    |
| LLM Providers    | OpenAI, Cohere             |
| Vector Database  | Qdrant (local persistence) |
| Application DB   | MongoDB                    |
| Document Parsing | LangChain                  |
| Configuration    | Pydantic Settings          |

---

## Getting Started (Local Development)

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites

- Python 3.11+
- Docker and Docker Compose (for running MongoDB)
- API keys from an LLM provider (e.g., OpenAI, Cohere)

### 2. Configuration

Copy the example environment file and fill in your credentials and desired configuration.

```bash
cp .env.example .env
```

Now, open the `.env` file and add your API keys and other settings.

### 3. Install Dependencies

It is recommended to use a virtual environment.

```bash
pip install -r requirements.txt
```

### 4. Run the Database

Start the MongoDB container using Docker Compose.

```bash
cd docker
docker-compose up -d
```

## Remove volumes

### 5. Run the Application

Navigate to the `src` directory and start the FastAPI server.

```bash
sudo docker volume rm $(sudo docker volume ls -q)
cd src
uvicorn main:app --reload
```

### Remove all

The API will be available at `http://127.0.0.1:8000/docs`.

```bash
 sudo docker system prune --all
```
