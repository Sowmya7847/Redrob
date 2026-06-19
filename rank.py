import os
import sys
import argparse
import csv
import time

# Add current directory to path
workspace_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(workspace_dir)

from src.retrieval import retrieve_top_k_candidates
from src.embedding_utils import get_embedding_model
from src.re_ranker import re_rank_candidates

def main():
    parser = argparse.ArgumentParser(description="Redrob Candidate Ranking Engine")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl file")
    parser.add_argument("--out", required=True, help="Output path for submission CSV")
    args = parser.parse_args()
    
    start_time = time.time()
    
    # 1. Load Job Description
    jd_path = os.path.join(workspace_dir, "job_description.txt")
    if not os.path.exists(jd_path):
        print(f"Error: Job description text file not found at {jd_path}")
        sys.exit(1)
        
    print(f"Reading job description from {jd_path}...")
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()
        
    # 2. Stage 1: Fast Retrieval & Filtering
    print("\n--- Phase 1: Running Stage 1 Retrieval ---")
    retrieve_start = time.time()
    # Retrieve top 3000 survivors
    survivors = retrieve_top_k_candidates(args.candidates, k=3000)
    retrieve_duration = time.time() - retrieve_start
    print(f"Stage 1 completed. Retrieved {len(survivors)} candidates in {retrieve_duration:.2f} seconds.")
    
    if not survivors:
        print("Error: No candidates survived Stage 1 filtering!")
        sys.exit(1)
        
    # 3. Load Offline Embedding Model
    print("\n--- Phase 2: Loading Offline Embedding Model ---")
    model_load_start = time.time()
    model_dir = os.path.join(workspace_dir, "model_cache", "all-MiniLM-L6-v2")
    model = get_embedding_model(model_dir)
    model_load_duration = time.time() - model_load_start
    print(f"Model loaded in {model_load_duration:.2f} seconds.")
    
    # 4. Stage 2: Detailed Re-ranking & Semantic Matching
    print("\n--- Phase 3: Running Stage 2 Re-ranking ---")
    re_rank_start = time.time()
    top_100 = re_rank_candidates(survivors, model, jd_text)
    re_rank_duration = time.time() - re_rank_start
    print(f"Stage 2 completed in {re_rank_duration:.2f} seconds.")
    
    # 5. Output Submission CSV
    print(f"\nWriting Top 100 ranked candidates to {args.out}...")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for idx, item in enumerate(top_100):
            # Rank is 1-indexed
            rank = idx + 1
            # Print score to 4 decimal places
            score_str = f"{item['score']:.4f}"
            writer.writerow([item["candidate_id"], rank, score_str, item["reasoning"]])
            
    total_duration = time.time() - start_time
    print(f"\nRanking process completed successfully in {total_duration:.2f} seconds.")
    print(f"Output saved to: {args.out}")

if __name__ == "__main__":
    main()
