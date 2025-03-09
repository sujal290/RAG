import { useState } from "react";

export default function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const uploadPdf = async () => {
    if (!file) return alert("Please select a PDF file.");
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        setUploadSuccess(true);
        alert("PDF uploaded successfully!");
      } else {
        alert("Upload failed!");
      }
    } catch (error) {
      console.error("Upload error:", error);
      alert("Error uploading file.");
    }
  };

  const askQuestion = async () => {
    if (!question) return alert("Please enter a question.");
    
    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();
      setAnswer(data.answer);
    } catch (error) {
      console.error("Error fetching answer:", error);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
      <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-lg">
        <h1 className="text-2xl font-semibold mb-4">PDF AI Assistant</h1>
        
        <input type="file" accept="application/pdf" onChange={handleFileChange} className="mb-4" />
        <button onClick={uploadPdf} className="bg-blue-600 text-white px-4 py-2 rounded-lg mb-4">Upload PDF</button>

        {uploadSuccess && (
          <div className="mt-4">
            <input 
              type="text" 
              placeholder="Ask a question..." 
              value={question} 
              onChange={(e) => setQuestion(e.target.value)} 
              className="border p-2 w-full rounded-lg"
            />
            <button onClick={askQuestion} className="bg-green-600 text-white px-4 py-2 rounded-lg mt-2">Get Answer</button>
          </div>
        )}

        {answer && (
          <div className="mt-4 p-4 bg-gray-200 rounded-lg">
            <strong>Answer:</strong> {answer}
          </div>
        )}
      </div>
    </div>
  );
}
