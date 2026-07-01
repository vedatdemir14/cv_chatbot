import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FastEmbedEmbeddings
from llm import get_llm_client

VECTOR_DB_PATH = "vectorstore"

conversation_memory = []

# Load vectorstore globally
vectorstore = None

# Single shared Groq client (reads GROQ_API_KEY / GROQ_MODEL from env)
llm_client = get_llm_client()


def get_vectorstore():
    global vectorstore
    if vectorstore is None:
        vectorstore = load_vectorstore()
    return vectorstore


def load_vectorstore():
    # Must match the embedding model used in ingest.py (fastembed/ONNX,
    # no torch -> low memory footprint)
    embeddings = FastEmbedEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
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
    docs = vs.similarity_search(role, k=4)
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
    answer = llm_client.generate(prompt, max_tokens=max_tokens, temperature=temperature)
    if answer is None:
        return "⚠️ The AI backend is currently unavailable. Please check the GROQ_API_KEY configuration."
    return answer


def ask_question(question: str) -> str:
    vs = get_vectorstore()
    docs = vs.similarity_search(question, k=3)
    context = "\n\n".join(d.page_content for d in docs)

    memory_context = ""
    if conversation_memory:
        memory_context = "\n\nPrevious conversation:\n" + "\n".join(conversation_memory[-2:])
        memory_context += "\n\nUse this context to make your response more natural."

    prompt = f"""
{memory_context}

{build_prompt(context, question)}
"""

    answer = query_llm(prompt, temperature=0.7, max_tokens=300)

    conversation_memory.append(f"Q: {question}\nA: {answer}")
    # Keep only last 4 conversations to avoid too long context
    if len(conversation_memory) > 4:
        conversation_memory.pop(0)

    return answer


def generate_why_hire() -> str:
    vs = get_vectorstore()
    docs = vs.similarity_search(
        "skills experience projects impact achievements", k=4
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
