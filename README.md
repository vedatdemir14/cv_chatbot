# 🤖 AI CV Chatbot

RAG-based chatbot that answers questions about CV and projects using open-source LLMs and vector search.

## 🎯 Overview

This chatbot uses **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware answers based solely on your CV and project information. It prevents hallucination by grounding all responses in the provided data.

## 🏗️ Architecture

```
User Question
      ↓
FastAPI Backend
      ↓
Query Embedding (sentence-transformers)
      ↓
FAISS Vector Search
      ↓
Relevant Chunks Retrieved
      ↓
Prompt Template with Context
      ↓
Open-Source LLM (Mistral-7B via Ollama)
      ↓
Answer
```

## 🧩 Components

- **LLM**: Mistral-7B-Instruct (local inference via Ollama)
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Database**: FAISS (local, fast, free)
- **Backend**: FastAPI
- **RAG Pipeline**: Custom implementation with context retrieval

## 📁 Project Structure

```
ai-cv-chatbot/
│
├── data/
│   ├── cv.txt          # CV information
│   ├── projects.txt    # Project descriptions
│   └── skills.txt      # Skills and technologies
│
├── ingest.py           # Data ingestion → FAISS index
├── rag.py              # RAG retrieval + generation
├── llm.py              # Ollama LLM client
├── app.py              # FastAPI backend
│
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🚀 Setup

### Prerequisites

1. **Python 3.11+**
2. **Ollama** installed and running
   ```bash
   # Install Ollama from https://ollama.ai
   # Pull Mistral model
   ollama pull mistral:7b-instruct
   # Start Ollama server
   ollama serve
   ```

### Installation

1. **Clone and navigate to project**
   ```bash
   cd cv_chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare your data**
   - Edit `data/cv.txt` with your CV information
   - Edit `data/projects.txt` with your projects
   - Edit `data/skills.txt` with your skills

4. **Ingest data into vector database**
   ```bash
   python ingest.py
   ```
   This creates `faiss_index.bin` and `metadata.txt`.

5. **Start the API server**
   ```bash
   python app.py
   ```
   Server runs on `http://localhost:8000`

## 🌐 Publish (Free) on GitHub

This repo can be published **for free** as:
- **Frontend**: GitHub Pages (static hosting)
- **Backend (FastAPI + Ollama)**: runs locally (GitHub Pages cannot run Python/LLMs)

### 1) Create a public GitHub repo and push

```bash
cd cv_chatbot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### 2) Enable GitHub Pages for the frontend

This repo includes a GitHub Actions workflow at `.github/workflows/deploy-frontend.yml` that builds the Vite app in `frontend/` and deploys it to **GitHub Pages** automatically on every push to `main`.

In GitHub:
- Go to **Settings → Pages**
- Under **Build and deployment**, select **GitHub Actions**

After the workflow completes, your site will be available at:
- `https://<your-username>.github.io/<your-repo>/`

### 3) Point the frontend to a backend (optional)

By default the frontend uses `http://127.0.0.1:8000`.
If you later host the backend publicly, set:
- **Vite env var**: `VITE_API_URL` (example: `https://your-api.example.com`)


## 📡 API Usage

### Ask a Question

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What programming languages do you know?"}'
```

**Response:**
```json
{
  "answer": "Based on the provided context, I know Python, JavaScript, and SQL.",
  "sources": ["skills.txt", "cv.txt"],
  "chunks": [
    {
      "source": "skills.txt",
      "text": "Programming Languages: Python, JavaScript, SQL",
      "relevance_score": 0.15
    }
  ]
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI.

## 🐳 Docker

### Build and Run

```bash
# Build image
docker build -t cv-chatbot .

# Run container
docker run -p 8000:8000 cv-chatbot
```

**Note**: For Docker, you'll need to run Ollama separately or use a Docker Compose setup.

## 🔧 Configuration

### Change LLM Model

Edit `llm.py`:
```python
DEFAULT_MODEL = "phi3:mini"  # or any Ollama model
```

### Adjust Retrieval

Edit `rag.py`:
```python
TOP_K = 5  # Retrieve more/fewer chunks
```

### Change Embedding Model

Edit `ingest.py` and `rag.py`:
```python
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Larger, more accurate
```

## 🎓 Key Features

✅ **No Hallucination**: Answers only from provided context  
✅ **Open-Source**: Uses free, local LLMs  
✅ **Fast**: FAISS vector search is extremely fast  
✅ **Scalable**: Easy to add more data sources  
✅ **Production-Ready**: FastAPI, Docker, proper error handling  

## 📝 Data Format

Data files should contain plain text, one sentence per line or paragraph format:

```
Your CV information here.
Multiple sentences are fine.
They will be chunked automatically.
```

## 🐛 Troubleshooting

### "FAISS index not found"
Run `python ingest.py` first.

### "Cannot connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check if model is installed: `ollama list`
- Install model: `ollama pull mistral:7b-instruct`

### "Model not found"
Install the model in Ollama:
```bash
ollama pull mistral:7b-instruct
```

## 📚 Technologies

- **FastAPI**: Modern Python web framework
- **FAISS**: Facebook AI Similarity Search
- **sentence-transformers**: State-of-the-art embeddings
- **Ollama**: Local LLM inference
- **Mistral-7B**: Open-source instruction-tuned LLM

## 🎯 Use Cases

- Personal portfolio chatbot
- CV/interview preparation
- Project showcase
- Knowledge base Q&A

## 📄 License

MIT

---

**Built with ❤️ using RAG and open-source AI**



