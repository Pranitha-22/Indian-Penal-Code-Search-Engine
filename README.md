# ⚖️ AI-Powered Indian Penal Code Legal Assistant

An intelligent legal search and reasoning system built from raw IPC data using NLP and hybrid AI retrieval techniques.

---

## 🧠 Key Highlights

- 🔍 Hybrid Search Engine (BM25 + Semantic Embeddings)
- 🤖 AI-Powered Legal Answer Generation
- 📊 Structured IPC dataset built from raw PDF
- ⚡ Real-time FastAPI backend with optimized retrieval
- 🧠 Explainable AI with reasoning and keyword matching
- 🌐 Clean UI for legal query interaction

---

## 🚀 What Makes This Project Unique

Unlike traditional keyword-based systems, this project:

- Understands **natural language queries**
- Performs **semantic search using transformers**
- Provides **context-aware legal explanations**
- Includes **reasoning behind results (Explainable AI)**

---

## 🧠 System Architecture

User Query  
→ Query Normalization  
→ Hybrid Retrieval (BM25 + Embeddings)  
→ Section Ranking  
→ AI Answer Generation  
→ Explanation + Reasoning  
→ Frontend Display  

---

## 📊 Core Features

- Section-based legal search  
- IPC punishment extraction  
- Bail / Cognizable classification  
- Related sections recommendation  
- Intelligent query understanding  
- Explainable AI outputs  

---

## 🛠 Tech Stack

### Backend
- FastAPI  
- Python  

### NLP & AI
- Sentence Transformers  
- BM25  
- Scikit-learn  
- FAISS  

### Data Processing
- Pandas  
- Numpy  

### Frontend
- HTML, CSS, JavaScript  

---

## 📁 Dataset

- Source: Indian Penal Code PDF  
- Converted into structured dataset with:
  - Section  
  - Title  
  - Law Text  
  - Punishment  
  - Keywords  

---

## ▶️ Run Locally

```bash
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload
