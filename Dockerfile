# Use a small Python base image
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# 1) System deps: clang/llvm for C/C++, curl for rustup, build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    clang \
    llvm \
    build-essential \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# 2) Install Rust (for .rs files)
# Non-interactive install of rustc via rustup
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
    sh -s -- -y --default-toolchain stable && \
    echo 'export PATH="/root/.cargo/bin:$PATH"' >> /etc/profile.d/rust.sh

# Make sure rustc is on PATH for all subsequent commands
ENV PATH="/root/.cargo/bin:${PATH}"

# 3) Set workdir
WORKDIR /app

# 4) Install Python dependencies
# Make sure requirements.txt includes:
# fastapi, uvicorn, pandas, numpy, scikit-learn, joblib, tqdm, psutil, etc.
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copy application code
COPY src ./src
COPY backend ./backend
COPY data ./data

# 6) Ensure Python can find the src package
ENV PYTHONPATH=/app

# 7) Expose backend port
EXPOSE 8080

# 8) Start FastAPI with uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
