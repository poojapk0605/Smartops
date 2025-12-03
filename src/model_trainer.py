import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

ROOT = Path(__file__).resolve().parent.parent

FEATURES_CSV = ROOT / "data" / "features.csv"
RESULTS_CSV = ROOT / "data" / "results.csv"
MODEL_PATH = ROOT / "data" / "model.pkl"


def compute_balanced_metric(df):
    """
    Compute normalized runtime, size, compile time, and balanced score.
    """

    scaler = MinMaxScaler()

    df[["runtime_norm", "binary_norm", "compile_norm"]] = scaler.fit_transform(
        df[["runtime", "binary_size", "compile_time"]]
    )

    # Define weights (runtime=60%, size=30%, compile time=10%)
    w_runtime = 0.6
    w_size = 0.3
    w_compile = 0.1

    df["balanced_score"] = (
        w_runtime * df["runtime_norm"]
        + w_size * df["binary_norm"]
        + w_compile * df["compile_norm"]
    )

    return df


def label_best_flags(df):
    """
    For each file, assign the flag that has the lowest balanced score.
    """

    best_rows = (
        df.loc[df.groupby("file")["balanced_score"].idxmin()]
        .reset_index(drop=True)
    )

    return best_rows[["file", "flag"]]


def main():
    print("🔍 Loading datasets...")

    feats = pd.read_csv(FEATURES_CSV)
    results = pd.read_csv(RESULTS_CSV)

    print("➡️ Merging features + results...")
    df = pd.merge(results, feats, on="file")

    print("➡️ Computing balanced metric...")
    df = compute_balanced_metric(df)

    print("➡️ Determining best flags for each file...")
    best_flags = label_best_flags(df)

    df = pd.merge(df, best_flags, on=["file", "flag"], how="left", indicator=True)
    df["is_best"] = df["_merge"] == "both"
    df.drop(columns=["_merge"], inplace=True)

    print("➡️ Preparing training data...")

    feature_columns = [
        "instruction_count", "load_count", "store_count", "arith_count",
        "branch_count", "cmp_count", "function_count", "basic_blocks",
        "loop_markers"
    ]

    X = df[feature_columns]
    y = df["is_best"].astype(int)

    # We convert flag into a class label
    df["flag_class"] = df["flag"].astype("category").cat.codes
    y_flag = df["flag_class"]

    # Train only on rows where that flag is best
    train_df = df.loc[df["is_best"] == True]
    X_train = train_df[feature_columns]
    y_train = train_df["flag"]

    print("➡️ Training RandomForest model...")
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    print("➡️ Saving model...")
    joblib.dump(model, MODEL_PATH)

    print("\n🎉 Training Completed!")
    print(f"📦 Model saved to: {MODEL_PATH}\n")

    print("➡️ Best flags found per file:")
    print(best_flags)

    print("\n📊 Full dataset with scores ready for analysis.")
    print("You can view it in a notebook or CSV.")


if __name__ == "__main__":
    main()
