import os
import subprocess
import time
from pathlib import Path
import pandas as pd

FLAGS = ["-O0", "-O1", "-O2", "-O3", "-Os"]

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "data" / "benchmarks"
OUTPUT_CSV = ROOT / "data" / "results.csv"
BIN_DIR = ROOT / "data" / "bin"

BIN_DIR.mkdir(exist_ok=True)

RUST_OPT_MAP = {
    "-O0": "0",
    "-O1": "1",
    "-O2": "2",
    "-O3": "3",
    "-Os": "s",
}


def run_command(command: list, timeout: int = 30):
    start = time.time()
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=timeout)
        return True, time.time() - start, ""
    except subprocess.TimeoutExpired:
        return False, None, "TimeoutExpired"
    except subprocess.CalledProcessError as e:
        return False, None, e.stderr.decode("utf-8", errors="ignore")


def measure_runtime(binary_path: Path, timeout: int = 10):
    start = time.time()
    try:
        subprocess.run([str(binary_path)], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       timeout=timeout)
        return True, time.time() - start, ""
    except subprocess.TimeoutExpired:
        return False, None, "TimeoutExpired"
    except subprocess.CalledProcessError as e:
        return False, None, e.stderr.decode("utf-8", errors="ignore")


def build_compile_command(src_file: Path, flag: str, bin_path: Path):
    ext = src_file.suffix
    if ext == ".c":
        return ["clang", flag, str(src_file), "-o", str(bin_path)]
    elif ext == ".cpp":
        return ["clang++", flag, str(src_file), "-o", str(bin_path)]
    elif ext == ".rs":
        opt = RUST_OPT_MAP[flag]
        # rustc uses -C opt-level=<0|1|2|3|s|z>
        return ["rustc", str(src_file), f"-Copt-level={opt}", "-o", str(bin_path)]
    else:
        raise ValueError(f"Unsupported source extension: {ext}")


def benchmark_file(src_file: Path):
    results = []
    base_name = src_file.stem
    lang = src_file.suffix

    for flag in FLAGS:
        bin_name = f"{base_name}_{flag.replace('-', '')}"
        bin_path = BIN_DIR / bin_name

        compile_cmd = build_compile_command(src_file, flag, bin_path)

        # Compile
        ok, compile_time, error = run_command(compile_cmd)
        if not ok:
            results.append({
                "file": base_name,
                "language": lang,
                "flag": flag,
                "compile_time": None,
                "runtime": None,
                "binary_size": None,
                "status": f"compile_error: {error}",
            })
            continue

        # Run
        ok, runtime, error = measure_runtime(bin_path)
        if not ok:
            results.append({
                "file": base_name,
                "language": lang,
                "flag": flag,
                "compile_time": round(compile_time, 5),
                "runtime": None,
                "binary_size": bin_path.stat().st_size if bin_path.exists() else None,
                "status": f"runtime_error: {error}",
            })
            continue

        # Success
        results.append({
            "file": base_name,
            "language": lang,
            "flag": flag,
            "compile_time": round(compile_time, 5),
            "runtime": round(runtime, 5),
            "binary_size": bin_path.stat().st_size,
            "status": "ok",
        })

    return results


def main():
    print("Running SmartOpt Benchmark Runner...\n")

    all_results = []

    for ext in ("*.c", "*.cpp", "*.rs"):
        for src in SRC_DIR.glob(ext):
            print(f"Benchmarking {src.name}")
            file_results = benchmark_file(src)
            all_results.extend(file_results)

    df = pd.DataFrame(all_results)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"\n✅ Benchmarking completed!")
    print(f"📄 Results saved to: {OUTPUT_CSV}")
    print(f"📦 Binaries stored in: {BIN_DIR}")


if __name__ == "__main__":
    main()
