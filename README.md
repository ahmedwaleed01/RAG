## Install Requirments

# RAG API Backend

```bash
pip install -r requirements.txt
```

This project is a Python-based backend for a **Retrieval-Augmented Generation (RAG)** system, built using the **FastAPI** framework. It provides a complete pipeline to upload documents, process them into searchable chunks, and perform semantic searches on the content.

## Run FastApi Server

## Core Features

```bash
uvicorn main:app --reload
```

- **Project-Based Workspaces:** Isolates documents and indexes using a `project_id`.
- **File Upload:** Supports `.pdf` and `.txt` file uploads.
- **Document Processing:** Splits documents into smaller, overlapping text chunks using `langchain`.
- **Vector Indexing:** Converts text chunks into embeddings and stores them in a vector database for semantic search.
- **Semantic Search:** Allows users to query the indexed content with natural language.
- **Pluggable Architecture:** Easily switch between different LLM providers (OpenAI, Cohere) and Vector Databases (Qdrant) through a factory pattern.
