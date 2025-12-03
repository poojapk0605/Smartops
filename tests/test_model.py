from src.smartopt import analyze_source
from pathlib import Path
import tempfile

def test_model_loads():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as tmp:
        tmp.write(b"int main(){return 0;}")
        path = Path(tmp.name)
    
    flag, stats = analyze_source(path)
    assert flag in ["-O0","-O1","-O2","-O3","-Os"]
