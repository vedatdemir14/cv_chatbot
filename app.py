from fastapi import FastAPI
from pydantic import BaseModel
from rag import ask_question, generate_why_hire, generate_recruiter_summary
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="AI CV Chatbot API",
    description="RAG-based personal CV chatbot using open-source LLMs",
    version="1.0.0"
    
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str

class RoleRequest(BaseModel):
    role: str

    
@app.get("/why-hire")
def why_should_we_hire():
    answer = generate_why_hire()
    return {"answer": answer}


@app.post("/ask", response_model=AnswerResponse)
def ask_cv_bot(request: QuestionRequest):
    answer = ask_question(request.question)
    return {"answer": answer}


@app.get("/")
def root():
    return {"status": "AI CV Chatbot API is running"}

@app.post("/summary")
def recruiter_summary(req: RoleRequest):
    summary = generate_recruiter_summary(req.role)
    return {"summary": summary}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

