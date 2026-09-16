"""
Stage 1-2: Load raw resumes/JDs and clean the text.

Usage:
    python src/preprocess.py --input data/raw/resumes.csv --output data/processed/resumes_clean.csv
"""

import argparse
import re
import pandas as pd


def clean_text(text: str) -> str:
    """Lowercase, strip emails/phone numbers/urls, collapse whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"\S+@\S+", " ", text)                     # emails
    text = re.sub(r"http\S+|www\.\S+", " ", text)             # urls
    text = re.sub(r"\+?\d[\d\-\s()]{7,}\d", " ", text)         # phone numbers
    text = re.sub(r"[^a-z0-9\s.,]", " ", text)                 # keep basic punctuation
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_and_clean(input_path: str, text_column: str) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    if text_column not in df.columns:
        raise ValueError(
            f"Column '{text_column}' not found. Available columns: {list(df.columns)}"
        )
    df["clean_text"] = df[text_column].apply(clean_text)
    df = df[df["clean_text"].str.len() > 20].reset_index(drop=True)  # drop near-empty rows
    return df


def main():
    parser = argparse.ArgumentParser(description="Clean resume/JD text data.")
    parser.add_argument("--input", required=True, help="Path to raw CSV file")
    parser.add_argument("--output", required=True, help="Path to save cleaned CSV")
    parser.add_argument(
        "--text-column", default="Resume", help="Name of the column containing raw text"
    )
    args = parser.parse_args()

    df = load_and_clean(args.input, args.text_column)
    df.to_csv(args.output, index=False)
    print(f"Cleaned {len(df)} rows -> {args.output}")


if __name__ == "__main__":
    main()
