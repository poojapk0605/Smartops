import sys
import tempfile
from pathlib import Path
import os
import requests

# Allow importing src.smartopt
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from src.smartopt import analyze_source
import uvicorn
from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------
# TEMPORARY: Hardcode your HF API key for testing
# ---------------------------------------------------
HF_API_KEY = os.getenv("HF_API_KEY")



HF_MODEL_URL = "https://api-inference.huggingface.co/models/google/gemma-2b-it"


# ---------------------------------------------------
# 🔍 Language Detection
# ---------------------------------------------------
def detect_language_from_code(code: str) -> str:
    lower = code.lower()

    # Strong C++ signals
    cpp_markers = [
        "std::", "cout", "cin", "cerr",
        "#include <iostream>", "#include<iostream>",
        "using namespace std",
        "template<", "template <",
        "class ", "typename "
    ]
    if any(m in lower for m in cpp_markers):
        return ".cpp"

    # Rust detection
    rust_markers = [
        "fn ", "println!", "let ", "match ", "pub ",
        "impl ", "trait ", "::", "usize", "vec<"
    ]
    if any(m in lower for m in rust_markers):
        return ".rs"

    # Default → C
    return ".c"


# ---------------------------------------------------
# 🧠 Gemma LLM Explanation Wrapper
# ---------------------------------------------------
def explain_results(best_flag, stats, language):
    """
    Calls Gemma-2B-IT to generate a 2–3 sentence explanation.
    """

    if HF_API_KEY is None:
        return "⚠️ LLM explanation unavailable (HF_API_KEY not set)."

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are an expert compiler engineer. Explain why the optimization flag {best_flag} 
performed best for the provided source code.

Language detected: {language}

Benchmark results:
{stats}

Explain in 2–3 simple sentences so a beginner can understand.
"""

    payload = {"inputs": prompt}

    try:
        response = requests.post(HF_MODEL_URL, headers=headers, json=payload, timeout=30)
        out = response.json()

        # HuggingFace returns: [{"generated_text": "..."}]
        if isinstance(out, list) and "generated_text" in out[0]:
            return out[0]["generated_text"]
        else:
            return "⚠️ Could not extract explanation from model."
    except Exception as e:
        return f"⚠️ LLM error: {e}"


# ---------------------------------------------------
# FastAPI App
# ---------------------------------------------------
app = FastAPI(
    title="SmartOpt Backend",
    description="AI-powered Compiler Optimization Advisor (C, C++, Rust)",
    version="2.3.0"
)

# CORS for HuggingFace UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------
# Health Check
# ---------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "SmartOpt backend is running"}


# ---------------------------------------------------
# 📌 (1) Analyze Uploaded File
# ---------------------------------------------------
@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    content = await file.read()

    suffix = Path(file.filename).suffix or ".c"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    best_flag, stats = analyze_source(tmp_path)

    explanation = explain_results(best_flag, stats, suffix)

    return {
        "filename": file.filename,
        "language": suffix,
        "best_flag": best_flag,
        "flags": stats,
        "explanation": explanation
    }


# ---------------------------------------------------
# 📌 (2) Analyze Pasted Code (JSON)
# ---------------------------------------------------
@app.post("/analyze-code")
async def analyze_code(payload: dict = Body(...)):
    if "code" not in payload:
        return {"error": "Missing 'code' field in JSON body"}

    code = payload["code"]

    suffix = detect_language_from_code(code)

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(code.encode())
        tmp_path = Path(tmp.name)

    best_flag, stats = analyze_source(tmp_path)
    explanation = explain_results(best_flag, stats, suffix)

    return {
        "filename": tmp_path.name,
        "language": suffix,
        "best_flag": best_flag,
        "flags": stats,
        "explanation": explanation
    }


# ---------------------------------------------------
# Run Server
# ---------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8080)
