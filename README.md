# 🧠 SmartOpt — AI-Powered Compiler Optimization Advisor

SmartOpt is an experimental **AI-driven compiler optimization advisor** for **C, C++**, and **Rust**.  
It predicts the best compiler optimization flag using **LLVM IR feature extraction**, **machine learning models**, and **real benchmarking**.

---

## 🚀 Key Features
- ⚙️ ML-based optimization flag prediction  
- 🌐 Multi-language support (C, C++, Rust)  
- ⏱️ Real compile-time and runtime benchmarking  
- 💡 Optional LLM explanations (Gemma-2B-IT)  
- ☁️ Fully automated CI/CD using Jenkins + GCP Cloud Run  
- 🧩 Simple Hugging Face UI for user interaction  

---

## 🏗️ Architecture Overview

<img width="764" height="523" alt="Untitled Diagram drawio" src="https://github.com/user-attachments/assets/5c847936-ce9e-438b-80d9-7f03bb8a948f" />

**Tech Stack**
- Backend: FastAPI (Python)
- Frontend: Hugging Face / Gradio
- ML: scikit-learn / XGBoost
- DevOps: Jenkins, Docker, GCP Cloud Run
- Compiler Toolchain: GCC, Clang, Rustc
----
### ⚠️ Current Limitations
- Small workloads may show similar binary sizes  
- Math-heavy workloads not yet supported  
- Lightweight ML model (prototype-level)  
- Designed for proof-of-concept scale  
---
## 🧠 To Test Smartopt CLI
- Clone the repo
- Install LLvm, clang
- Create virtual environment : python3 -m venv venv
- Activate : source venv/bin/activate
- Install requirements : pip install -r requirements.txt
- Test benchmark generation : python3 src/benchmark_runner.py. This proves "Clang" is working by generating : "results.csv and binaries in data/bin/ "
- Test feature extractor : python3 src/feature_extractor.py. This should be generating :"ir/ directory with .ll files ,features.csv  "
- Test the trained model. It should be under data/model.pki and then run the command : python3 -m src.smartopt data/benchmarks/sort.c
- Expected Output :
  - 🚀 SmartOpt Analysis Started on: sort.c
  - 🔍 Generating LLVM IR...
  - 📊 Extracting features...
  - 🧠 Loading SmartOpt model...
  - ✨ Predicting best optimization flag...
  - ✅ SmartOpt Recommendation:
  - 👉 Best optimization flag: -O3
     
----
## 🧠 To Test using Docker
- Clone the repo
- Install docker
- Build the image : docker build -t smartopt-backend .
- Run the image :docker run -p 8082:8080 smartopt-backend
- Sample Test for C  : curl -X POST "http://localhost:8082/analyze-code" -H "Content-Type: application/json" -d '{"code": "int main(){ return 0; }"}'
- Sample Test for Rust : curl -X POST "http://localhost:8082/analyze-code" -H "Content-Type: application/json" -d '{"code": "fn main(){ println!(\"Hello\"); }"}'
- Sample Test for C++ : curl -X POST "http://localhost:8082/analyze-code" -H "Content-Type: application/json" -d "{\"code\": \"#include <iostream>\\nint main(){ std::cout << 5; }\"}"
- To check the Outputs: Please refer the Document "Smartopt.pdf"
  
------
  





