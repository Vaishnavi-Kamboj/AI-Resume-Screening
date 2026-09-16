"""
Stage 3: Extract skills, organizations, and dates from cleaned text using spaCy.

Install first:
    pip install spacy
    python -m spacy download en_core_web_sm

Usage:
    python src/extract_entities.py --input data/processed/resumes_clean.csv --output data/processed/resumes_entities.csv
"""

import argparse
import pandas as pd
import spacy

# A small starter skills list — expand this with a real skills taxonomy
# (e.g. from ESCO, LinkedIn Skills, or a Kaggle skills dataset) as you go.
SKILL_KEYWORDS = [
    "python", "java", "sql", "machine learning", "deep learning", "nlp",
    "tensorflow", "pytorch", "excel", "communication", "leadership",
    "aws", "docker", "react", "javascript", "data analysis", "spacy",
    "flask", "fastapi", "git", "linux", "power bi", "tableau",
]


def extract_row_entities(nlp, text: str) -> dict:
    doc = nlp(text)
    orgs = list({ent.text for ent in doc.ents if ent.label_ == "ORG"})
    dates = list({ent.text for ent in doc.ents if ent.label_ == "DATE"})
    found_skills = [kw for kw in SKILL_KEYWORDS if kw in text]
    return {
        "organizations": "; ".join(orgs),
        "dates": "; ".join(dates),
        "skills": "; ".join(found_skills),
    }


def main():
    parser = argparse.ArgumentParser(description="Extract entities from cleaned text.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--text-column", default="clean_text")
    args = parser.parse_args()

    nlp = spacy.load("en_core_web_sm")
    df = pd.read_csv(args.input)

    extracted = df[args.text_column].apply(lambda t: extract_row_entities(nlp, str(t)))
    extracted_df = pd.DataFrame(list(extracted))
    result = pd.concat([df, extracted_df], axis=1)

    result.to_csv(args.output, index=False)
    print(f"Extracted entities for {len(result)} rows -> {args.output}")


if __name__ == "__main__":
    main()
