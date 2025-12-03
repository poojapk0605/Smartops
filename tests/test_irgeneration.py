from src.feature_extractor import generate_ir
from pathlib import Path
import tempfile

def test_generate_ir():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as tmp:
        tmp.write(b"int main(){return 0;}")
        path = Path(tmp.name)
    
    ll = generate_ir(path)
    assert ll.exists()
    assert ll.read_text().strip() != ""
