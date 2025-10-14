# 🚀 Cerebras POC — Frontend UI

This directory contains the **Streamlit-based user interface (UI)** for the **Cerebras Proof of Concept (POC)** project.  
It provides an interactive front-end to visualize and test Cerebras API integrations and model outputs.

The frontend is designed to work alongside the `backend.py` FastAPI server in the parent directory.

---

## 🧩 Features
- Interactive Streamlit UI for experimentation and testing  
- Modular structure (`src/` folder) with separate utilities, components, and mock data  
- Integration ready with the FastAPI backend
- Support for both solo and comparison modes

---

## 🛠️ Prerequisites
Make sure you have the following installed:

- **Python 3.9 or higher**
- **pip** (Python package manager)

(Optional) Recommended: `venv` or `conda` for a clean virtual environment.

---

## 📦 Setup Instructions

### 1️⃣ Navigate to the Frontend Directory
```bash
cd cerebras/apps/chat/frontend
```

### 2️⃣ Create and Activate a Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Or on Windows:
# venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Streamlit App
```bash
streamlit run app.py
```

---

## 🔗 Integration with Backend

The frontend can be enhanced to integrate with the FastAPI backend (`../backend.py`) which provides:
- `/chat/solo` - Single provider chat completions
- `/chat/compare` - Comparison between providers  
- `/chat/stream` - WebSocket streaming
- `/health` - Health check endpoint
- `/metrics` - Prometheus metrics

To run both frontend and backend together:

1. **Terminal 1 (Backend):**
   ```bash
   cd cerebras/apps/chat
   uvicorn backend:app --reload --port 8000
   ```

2. **Terminal 2 (Frontend):**
   ```bash
   cd cerebras/apps/chat/frontend  
   streamlit run app.py
   ```
