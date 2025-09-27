import argparse, os, sys, json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validation", required=True, help="Path to validation.csv")
    args = ap.parse_args()

    if not os.path.isfile("dataset.csv"):
        sys.stderr.write("dataset.csv not found in current folder\n")
        sys.exit(1)
    if not os.path.isfile(args.validation):
        sys.stderr.write(f"Validation file not found: {args.validation}\n")
        sys.exit(1)

    df = pd.read_csv("dataset.csv")
    val_df = pd.read_csv(args.validation)

    req_cols = {"company_name", "exchange", "year", "text_excerpt", "label"}
    if not req_cols.issubset(df.columns):
        sys.stderr.write("dataset.csv missing required columns\n")
        sys.exit(1)
    if not {"text_excerpt", "label"}.issubset(val_df.columns):
        sys.stderr.write("validation.csv must contain columns: text_excerpt,label\n")
        sys.exit(1)

    X_train = df["text_excerpt"].astype(str)
    y_train = df["label"].astype(int)

    X_val = val_df["text_excerpt"].astype(str)
    y_val = val_df["label"].astype(int)

    vec = TfidfVectorizer(max_features=30000, ngram_range=(1, 2), lowercase=True)
    Xtr = vec.fit_transform(X_train)
    Xte = vec.transform(X_val)

    clf = LogisticRegression(max_iter=500, solver="liblinear")
    clf.fit(Xtr, y_train)

    y_pred = clf.predict(Xte)

    acc = float(accuracy_score(y_val, y_pred))
    prec, rec, f1, _ = precision_recall_fscore_support(y_val, y_pred, average="binary", zero_division=0)

    out = {
        "files_used_for_training": int(df["company_name"].nunique()),
        "exchanges_in_dataset": sorted(list(map(str, set(df["exchange"].astype(str))))),
        "accuracy": round(acc, 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
    }
    print(json.dumps(out))

if __name__ == "__main__":
    main()
