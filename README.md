# NLP-Driven Indian Penal Code Search Engine

## Legal Information Retrieval System using NLP

This project is a semantic search engine for navigating the Indian Penal Code (IPC).  
It enables intelligent retrieval of sections, punishments, and related offenses using NLP-based similarity ranking instead of simple keyword matching.

---

## Core Features

- Structured IPC dataset parsing
- Section-level indexing (main text, proviso, explanation, punishment)
- Keyword + similarity-based search
- FastAPI backend API
- Clean web interface
- Popular category filtering
- Ranked search results
- Optimized query response time

---

## System Architecture

User Query  
→ Text Preprocessing  
→ Vectorization (TF-IDF / Embeddings)  
→ Similarity Scoring  
→ Ranked Section Retrieval  
→ API Response  
→ Frontend Rendering  

---

## NLP Pipeline

- Text cleaning & normalization
- Tokenization
- TF-IDF vectorization
- Cosine similarity ranking
- Relevance-based result sorting

(Optional: if you used Sentence Transformers, mention it clearly.)

---

## Example Query

Input:
"What is punishment for kidnapping?"

Output:
- IPC Section 359–369
- Relevant punishment clauses
- Ranked related sections

---

## Technology Stack

### Backend
- Python
- FastAPI
- Pandas
- Scikit-learn

### NLP
- TF-IDF Vectorizer
- Cosine Similarity

### Frontend
- HTML
- CSS
- JavaScript

---

## Dataset

- Structured IPC CSV dataset
- Cleaned and tokenized for NLP processing
- Indexed by section number and category

---

## Run Locally

```bash
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload
```

Open in browser:

```
http://127.0.0.1:8000
```

---

## Engineering Highlights

- Designed legal text indexing pipeline
- Implemented similarity-based ranking mechanism
- Built API-based search architecture
- Optimized dataset cleaning and preprocessing
- Clean separation of backend and static assets

---

## Future Improvements

- Upgrade to transformer embeddings
- Add multilingual search
- Deploy as public legal search API
- Implement advanced query expansion
