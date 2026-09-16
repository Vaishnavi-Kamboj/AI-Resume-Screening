# Resume-Job Matching System

Semantic resume screening using Sentence-BERT embeddings and spaCy NER,
instead of plain keyword matching.

## Project structure

```
resume-matcher/
├── data/
│   ├── raw/            # place downloaded Kaggle CSVs here
│   └── processed/      # cleaned/intermediate outputs land here
├── src/
│   ├── preprocess.py       # Stage 1-2: load + clean text
│   ├── extract_entities.py # Stage 3: spaCy NER (skills, orgs, dates)
│   └── match.py             # Stage 4-5: embeddings + cosine similarity
├── models/              # saved embeddings / fine-tuned models (if any)
├── app/                 # Stage 6-7: API + deployment code goes here
└── notebooks/           # exploration, EDA, experiments
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install pandas scikit-learn spacy sentence-transformers fastapi uvicorn
python -m spacy download en_core_web_sm
```

## Suggested datasets (place raw CSVs in data/raw/)

- Resume vs. Job Description Matching Dataset (Kaggle)
- Resume Dataset (Kaggle, category-labeled resumes)
- Job Titles and Description (Kaggle)

## Running the pipeline

```bash
# 1-2. Clean resumes and job descriptions
python src/preprocess.py --input data/raw/resumes.csv --output data/processed/resumes_clean.csv --text-column Resume
python src/preprocess.py --input data/raw/jobs.csv --output data/processed/jobs_clean.csv --text-column Description

# 3. Extract entities (skills, orgs, dates) from resumes
python src/extract_entities.py --input data/processed/resumes_clean.csv --output data/processed/resumes_entities.csv

# 4-5. Generate embeddings and compute matches
python src/match.py --resumes data/processed/resumes_entities.csv --jobs data/processed/jobs_clean.csv --output data/processed/match_scores.csv --top-k 5
```

## Next steps (stages 6-7)

- Wrap `match.py` logic in a FastAPI endpoint (`app/main.py`) that accepts
  a resume + job description and returns a similarity score + ranked list.
- Containerize with Docker and deploy to Render/Railway/AWS, or build a
  quick Streamlit front-end for the college demo.
