from src.benchmark_runner import FLAGS, build_compile_command, run_command, BIN_DIR
from pathlib import Path
import tempfile

def test_all_flags_compile():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as tmp:
        tmp.write(b"int main(){return 0;}")
        path = Path(tmp.name)

    for flag in FLAGS:
        bin_path = BIN_DIR / f"test_{flag.replace('-', '')}"
        cmd = build_compile_command(path, flag, bin_path)
        ok, _, _ = run_command(cmd)
        assert ok
