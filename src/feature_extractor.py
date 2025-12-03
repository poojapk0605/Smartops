import os
import subprocess
from pathlib import Path
import pandas as pd
import re

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "data" / "benchmarks"
IR_DIR = ROOT / "data" / "ir"
OUTPUT_CSV = ROOT / "data" / "features.csv"

IR_DIR.mkdir(exist_ok=True)

FEATURES = [
    "instruction_count",
    "load_count",
    "store_count",
    "arith_count",
    "branch_count",
    "cmp_count",
    "function_count",
    "basic_blocks",
    "loop_markers",
]


def generate_ir(src_file: Path) -> Path:
    """
    Generate LLVM IR for C / C++ / Rust source file.
    Returns path to the .ll file.
    """
    src_file = Path(src_file)
    ll_file = IR_DIR / (src_file.stem + ".ll")

    if src_file.suffix == ".c":
        cmd = ["clang", "-O0", "-emit-llvm", "-S", str(src_file), "-o", str(ll_file)]
    elif src_file.suffix == ".cpp":
        cmd = ["clang++", "-O0", "-emit-llvm", "-S", str(src_file), "-o", str(ll_file)]
    elif src_file.suffix == ".rs":
        # rustc outputs <name>.ll by default when using --emit=llvm-ir
        cmd = ["rustc", str(src_file), "--emit=llvm-ir", "-o", str(ll_file)]
    else:
        raise ValueError(f"Unsupported source extension: {src_file.suffix}")

    subprocess.run(cmd, check=True)
    return ll_file


def extract_features_from_ir(ir_file: Path) -> dict:
    """Parse LLVM IR and extract features."""
    text = Path(ir_file).read_text()

    features = {
        "instruction_count": len(re.findall(r"\s[a-zA-Z]+\s", text)),
        "load_count": len(re.findall(r"\bload\b", text)),
        "store_count": len(re.findall(r"\bstore\b", text)),
        "arith_count": len(re.findall(r"\b(add|mul|sub|div)\b", text)),
        "branch_count": len(re.findall(r"\bbr\b", text)),
        "cmp_count": len(re.findall(r"\bicmp|fcmp\b", text)),
        "function_count": len(re.findall(r"\bdefine\b", text)),
        "basic_blocks": len(re.findall(r"\blabel\b", text)),
        "loop_markers": len(re.findall(r"llvm.loop", text)),
    }
    return features


def extract_features(ll_path: Path) -> pd.DataFrame:
    """
    Wrapper used by SmartOpt CLI.
    Takes .ll file path and returns a 1-row DataFrame.
    """
    feats = extract_features_from_ir(ll_path)
    df = pd.DataFrame([feats])
    return df


def main():
    print("🔍 Extracting LLVM IR features...")

    all_rows = []

    for ext in ("*.c", "*.cpp", "*.rs"):
        for src in SRC_DIR.glob(ext):
            print(f"➡️ Processing {src.name}")
            ir_file = generate_ir(src)
            feats = extract_features_from_ir(ir_file)
            feats["file"] = src.stem
            feats["language"] = src.suffix  # optional feature
            all_rows.append(feats)

    df = pd.DataFrame(all_rows)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"\n✅ Feature extraction complete!")
    print(f"📄 features.csv saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
