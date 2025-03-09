from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import os

app = FastAPI()

pdfs_directory = "uploaded_pdfs"

class Question(BaseModel):
    question: str

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not os.path.exists(pdfs_directory):
        os.makedirs(pdfs_directory)
    
    file_path = os.path.join(pdfs_directory, file.filename)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    return {"message": "PDF uploaded successfully!"}

@app.post("/ask")
async def ask_question(q: Question):
    # This should be replaced with actual AI logic
    return {"answer": f"Mock answer for: {q.question}"}
