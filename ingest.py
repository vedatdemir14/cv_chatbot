import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.embeddings import FastEmbedEmbeddings

DATA_DIR = "data"
VECTOR_DB_PATH = "vectorstore"


def load_documents():
    documents = []

    for file_name in os.listdir(DATA_DIR):
        if file_name.endswith(".txt"):
            file_path = os.path.join(DATA_DIR, file_name)

            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": file_name}
                )
            )

    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_documents(documents)


def create_vectorstore(chunks):
    # fastembed is ONNX-based (no torch), which keeps memory usage low enough
    # to run on Render's free 512MB instances.
    embedding_model = FastEmbedEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )

    vectorstore = FAISS.from_documents(
        chunks,
        embedding_model
    )

    vectorstore.save_local(VECTOR_DB_PATH)
    print(f"✅ Vector DB created and saved to '{VECTOR_DB_PATH}'")


def main():
    print("📥 Loading documents...")
    documents = load_documents()

    print("✂️ Splitting documents into chunks...")
    chunks = split_documents(documents)

    print("🧠 Creating embeddings & FAISS index...")
    create_vectorstore(chunks)


if __name__ == "__main__":
    main()
