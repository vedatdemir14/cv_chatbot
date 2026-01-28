import requests
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


VECTOR_DB_PATH = "vectorstore"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

conversation_memory = []

# Load vectorstore globally
vectorstore = None

def get_vectorstore():
    global vectorstore
    if vectorstore is None:
        vectorstore = load_vectorstore()
    return vectorstore

def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vectorstore


def build_prompt(context: str, question: str) -> str:
    return f"""
You are a friendly AI assistant representing a person's CV. Answer naturally and conversationally in English.

Rules:
- Use ONLY the CV context below. Never make up information.
- Be conversational and warm (avoid overly short, robotic answers).
- If information is missing, politely say it's not in the CV.
- Keep answers informative (2-4 sentences, longer if needed).

CV CONTEXT:
{context}

QUESTION: {question}

ANSWER (English, conversational):
"""
def generate_recruiter_summary(role: str) -> str:
    vs = get_vectorstore()
    docs = vs.similarity_search(role, k=4)  # Reduced from 6 to 4
    context = "\n\n".join(d.page_content for d in docs)

    prompt = f"""
Write a natural summary highlighting why this candidate fits the role: {role}

Rules:
- Use ONLY the CV context below.
- Write in English.
- Focus on relevant skills and experience.
- 3-4 sentences, natural and engaging.

CV CONTEXT:
{context}

SUMMARY:
"""
    return query_llm(prompt, temperature=0.7, max_tokens=250)


def query_llm(prompt: str, temperature: float = 0.7, max_tokens: int = 300) -> str:
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,  # Reduced for faster responses
            "top_p": 0.9,  # Nucleus sampling for faster generation
        }
    }

    response = requests.post(url, json=payload, timeout=60)  # Reduced timeout
    response.raise_for_status()

    data = response.json()
    return data["response"]

def ask_question(question: str) -> str:
    vs = get_vectorstore()
    docs = vs.similarity_search(question, k=3)  # Reduced from 5 to 3 for faster retrieval
    context = "\n\n".join(d.page_content for d in docs)

    memory_context = ""
    if conversation_memory:
        memory_context = "\n\nPrevious conversation:\n" + "\n".join(conversation_memory[-2:])  # Reduced from 3 to 2
        memory_context += "\n\nUse this context to make your response more natural."

    prompt = f"""
{memory_context}

{build_prompt(context, question)}
"""

    answer = query_llm(prompt, temperature=0.7, max_tokens=300)  # Faster generation

    conversation_memory.append(f"Q: {question}\nA: {answer}")
    # Keep only last 4 conversations to avoid too long context
    if len(conversation_memory) > 4:
        conversation_memory.pop(0)

    return answer
    
def generate_why_hire() -> str:
    vs = get_vectorstore()
    docs = vs.similarity_search(
        "skills experience projects impact achievements", k=4  # Reduced from 6 to 4
    )
    context = "\n\n".join(d.page_content for d in docs)

    prompt = f"""
Explain why this candidate should be hired. Write in English naturally and compellingly.

Rules:
- Use ONLY the CV context below.
- Write in English, warm and engaging.
- Focus on key strengths, experience, and achievements.
- 4-5 sentences, natural flow.

CV CONTEXT:
{context}

WHY SHOULD WE HIRE THIS CANDIDATE:
"""

    return query_llm(prompt, temperature=0.7, max_tokens=300).strip()


if __name__ == "__main__":
    print("🤖 AI CV Chatbot is ready!")
    while True:
        q = input("\n❓ Ask a question (type 'exit' to quit): ")
        if q.lower() == "exit":
            break

        response = ask_question(q)
        print("\n✅ Answer:\n", response)


