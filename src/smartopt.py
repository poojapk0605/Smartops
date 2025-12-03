import joblib
from pathlib import Path
import pandas as pd

from .feature_extractor import generate_ir, extract_features_from_ir
from .benchmark_runner import (
    FLAGS,
    build_compile_command,
    measure_runtime,
    run_command,
    BIN_DIR
)


ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "data" / "model.pkl"


def predict_flag(src_path: Path) -> str:
    """
    Legacy function — only returns single prediction.
    """
    src_path = Path(src_path)
    ll_path = generate_ir(src_path)
    feats = extract_features_from_ir(ll_path)
    X = pd.DataFrame([feats])

    model = joblib.load(MODEL_PATH)
    return model.predict(X)[0]


def analyze_source(src_path: Path):
    """
    New SmartOpt engine:
    - Extracts LLVM IR features
    - Predicts best optimization flag
    - Benchmarks all flags for this file

    Returns:
        best_flag : str
        flags : list[dict] (metrics table)
    """
    src_path = Path(src_path)

    # 1️⃣ Extract features → ML predict best flag
    ll_path = generate_ir(src_path)
    feats = extract_features_from_ir(ll_path)
    X = pd.DataFrame([feats])

    model = joblib.load(MODEL_PATH)
    best_flag = model.predict(X)[0]

    # 2️⃣ Benchmark all flags
    results = []
    for flag in FLAGS:
        bin_name = f"{src_path.stem}_tmp_{flag.replace('-', '')}"
        bin_path = BIN_DIR / bin_name

        # compile
        compile_cmd = build_compile_command(src_path, flag, bin_path)
        ok, compile_time, err = run_command(compile_cmd)
        if not ok:
            results.append({
                "flag": flag,
                "compile_time": None,
                "runtime": None,
                "binary_size": None,
                "status": f"compile_error: {err}"
            })
            continue

        # run
        ok, runtime, err = measure_runtime(bin_path)
        if not ok:
            size = bin_path.stat().st_size if bin_path.exists() else None
            results.append({
                "flag": flag,
                "compile_time": round(compile_time, 5),
                "runtime": None,
                "binary_size": size,
                "status": f"runtime_error: {err}"
            })
            continue

        results.append({
            "flag": flag,
            "compile_time": round(compile_time, 5),
            "runtime": round(runtime, 5),
            "binary_size": bin_path.stat().st_size,
            "status": "ok"
        })

    return best_flag, results


def cli():
    import argparse
    parser = argparse.ArgumentParser(description="SmartOpt CLI")
    parser.add_argument("source", help="Path to C/C++/Rust source file")
    args = parser.parse_args()

    best_flag, stats = analyze_source(args.source)

    print(f"\nSmartOpt result for {args.source}:")
    print(f"Best Flag: {best_flag}")
    print("All flags:")
    for row in stats:
        print(row)


if __name__ == "__main__":
    cli()
