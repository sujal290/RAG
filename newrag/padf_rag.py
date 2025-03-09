import os
import shutil
import streamlit as st
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pdfs_directory = "pdfs"

# Load Ollama embeddings and vector store
embeddings = OllamaEmbeddings(model="deepseek-r1:1.5b")
vector_store = InMemoryVectorStore(embeddings)
model = OllamaLLM(model="deepseek-r1:1.5b")

# Ensure directory exists
os.makedirs(pdfs_directory, exist_ok=True)

# Upload PDF API
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(pdfs_directory, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "PDF uploaded successfully", "file_path": file_path}

# Load and index PDF
def process_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    chunked_documents = text_splitter.split_documents(documents)
    vector_store.add_documents(chunked_documents)

# Question model
class QuestionRequest(BaseModel):
    question: str

# Retrieve answer API
@app.post("/ask")
async def answer_question(request: QuestionRequest):
    related_docs = vector_store.similarity_search(request.question)

    if not related_docs:
        return {"answer": "I don't know the answer."}

    context = "\n\n".join([doc.page_content for doc in related_docs])
    prompt = ChatPromptTemplate.from_template(
        "You are an assistant. Use the following context to answer: {context}. Question: {question}. Answer:"
    )
    
    chain = prompt | model
    answer = chain.invoke({"question": request.question, "context": context})

    return {"answer": answer}
