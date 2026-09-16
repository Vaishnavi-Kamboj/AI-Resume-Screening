"""
Stage 4-5: Generate Sentence-BERT embeddings and compute resume-JD similarity.

Install first:
    pip install sentence-transformers scikit-learn

Usage:
    python src/match.py --resumes data/processed/resumes_entities.csv \
                         --jobs data/processed/jobs_clean.csv \
                         --output data/processed/match_scores.csv \
                         --top-k 5
"""

import argparse
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def embed_texts(model: SentenceTransformer, texts: list[str]):
    return model.encode(texts, show_progress_bar=True, convert_to_numpy=True)


def main():
    parser = argparse.ArgumentParser(description="Match resumes to job descriptions.")
    parser.add_argument("--resumes", required=True)
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--resume-text-col", default="clean_text")
    parser.add_argument("--job-text-col", default="clean_text")
    parser.add_argument("--top-k", type=int, default=5, help="Top matches per job")
    args = parser.parse_args()

    resumes = pd.read_csv(args.resumes)
    jobs = pd.read_csv(args.jobs)

    model = SentenceTransformer("all-MiniLM-L6-v2")  # fast, strong baseline

    resume_embeddings = embed_texts(model, resumes[args.resume_text_col].astype(str).tolist())
    job_embeddings = embed_texts(model, jobs[args.job_text_col].astype(str).tolist())

    sim_matrix = cosine_similarity(job_embeddings, resume_embeddings)

    rows = []
    for job_idx, job_row in jobs.iterrows():
        scores = sim_matrix[job_idx]
        top_indices = scores.argsort()[::-1][: args.top_k]
        for rank, resume_idx in enumerate(top_indices, start=1):
            rows.append({
                "job_index": job_idx,
                "rank": rank,
                "resume_index": resume_idx,
                "similarity_score": round(float(scores[resume_idx]), 4),
            })

    results = pd.DataFrame(rows)
    results.to_csv(args.output, index=False)
    print(f"Saved top-{args.top_k} matches per job -> {args.output}")


if __name__ == "__main__":
    main()
