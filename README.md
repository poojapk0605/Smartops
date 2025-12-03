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


**Tech Stack**
- Backend: FastAPI (Python)
- Frontend: Hugging Face / Gradio
- ML: scikit-learn / XGBoost
- DevOps: Jenkins, Docker, GCP Cloud Run
- Compiler Toolchain: GCC, Clang, Rustc

---

## 🧠 Example Usage
**API Endpoint:**  
`POST /analyze-code`

**Sample Payload:**
```json
{"code": "int main() { return 0; }"}

{"language": ".c", "best_flag": "-O2", "explanation": "The -O2 flag balances speed and size efficiently."}

**Current Limitations**
- Small workloads may show similar binary sizes
- Math-heavy workloads not yet supported
- Lightweight ML model (prototype-level)
- Designed for proof-of-concept scale