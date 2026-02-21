# ⚖️ NLP-Driven Indian Penal Code Search Engine
## 📘 Legal Information Retrieval System Built from Raw IPC PDF

This project converts the Indian Penal Code (IPC) from raw PDF format into a structured dataset and builds a searchable web-based legal information retrieval system.

The system enables users to search IPC sections, punishments, and offenses through a clean UI powered by a backend NLP pipeline.

---

## 🧠 Project Pipeline

IPC PDF  
→ Text Extraction  
→ Section Parsing & Structuring  
→ Dataset Creation (CSV)  
→ Search Engine Backend  
→ Web UI Rendering  

---

## 📂 Data Engineering

- Extracted raw IPC content from PDF
- Cleaned and structured into section-level dataset
- Separated components:
  - Main Text  
  - Proviso  
  - Explanation  
  - Punishment  
  - Chapter  
- Generated searchable CSV dataset

This transforms unstructured legal text into structured machine-readable data.

---

## 🔍 Core Features

- Structured IPC dataset from PDF source  
- Section-based indexing  
- Keyword-driven search  
- Ranked section retrieval  
- Clean, responsive UI  
- Popular legal category shortcuts  
- Fast query response  

---

## ⚙️ Search Engine Workflow

User Query  
→ Text Preprocessing  
→ Dataset Search  
→ Section Matching  
→ Ranked Results  
→ Frontend Display  

---

## 🖥️ User Interface

- Minimal legal search layout  
- Prominent search bar  
- Category-based navigation  
- Section result formatting  
- Clear punishment display  

---

## 🛠️ Technology Stack

### 🐍 Backend
- Python  
- FastAPI  
- Pandas  

### 📊 Data Processing
- Custom PDF-to-dataset parser  
- CSV-based indexing  

### 🌐 Frontend
- HTML  
- CSS  
- JavaScript  

---

## 📁 Dataset

- Source: Indian Penal Code (official PDF)
- Converted into structured CSV format
- Indexed by section number and legal category

---

## ▶️ Run Locally

```bash
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload
```

Open in browser:

```
http://127.0.0.1:8000
```

---

## 🚀 Engineering Highlights

- Built automated PDF-to-dataset conversion pipeline  
- Designed legal document structuring logic  
- Implemented searchable backend architecture  
- Built full-stack legal search interface  
- Clean separation of data processing and UI layers  

---

## 🔮 Future Improvements

- Add TF-IDF ranking  
- Upgrade to embedding-based semantic search  
- Add multilingual query support  
- Deploy as public legal API  
