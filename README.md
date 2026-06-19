# Redrob Recruiter Dashboard & Candidate Ranking System

This repository contains a production-ready recruiter-facing dashboard and a high-performance candidate ranking engine for the Redrob Intelligent Candidate Discovery & Ranking Challenge.

---

## 1. Folder Structure

```
.
├── app.py                      # Streamlit dashboard application (6 pages)
├── sample_data_loader.py       # Candidate dataset loader, offline cache creator, and sandbox evaluator
├── download_model.py           # Pre-computation model downloader
├── rank.py                      # Batch ranking command-line entrypoint
├── requirements.txt            # Python package dependencies
├── submission_metadata.yaml    # Hackathon metadata declarations
├── validate_submission.py      # Format validator for submission.csv
├── candidates.jsonl            # Candidates pool (100,000 candidates)
├── job_description.txt         # Plain text job description
├── .streamlit/
│   └── config.toml             # Streamlit design and theme settings
├── src/
│   ├── retrieval.py            # Stage 1: Feature Extraction & Retrieval
│   ├── product_scorer.py       # Product Experience Scorer
│   ├── risk_engine.py          # Risk Scoring Engine
│   ├── embedding_utils.py      # SentenceTransformers loading & matching
│   └── re_ranker.py            # Stage 2: Pre-ranking, Re-ranking & Tie-breaking
└── model_cache/
    └── all-MiniLM-L6-v2/       # Offline SentenceTransformer weights
```

---

## 2. Local Execution Instructions

### Step 1: Install Dependencies
Install all required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Step 2: Pre-compute Model Cache
Download and cache the `all-MiniLM-L6-v2` model weights locally so that the application can run 100% offline:
```bash
python download_model.py
```

### Step 3: Run the Ranking Batch (Optional)
Generate the `submission.csv` via the batch ranking script:
```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

### Step 4: Run the Streamlit Application
Start the recruiter web interface:
```bash
streamlit run app.py
```
*(Note: On the very first run, the app will run the ranking engine on `candidates.jsonl` to pre-calculate and cache the Top 1000 candidates. This takes ~25 seconds. Subsequent loads are near-instantaneous (< 2 seconds) using the generated `data_cache.json` file).*

---

## 3. Deployment Instructions

### A. Streamlit Cloud
1. Push this repository to a GitHub repository.
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io/) and click "New app".
3. Select your repository, branch, and specify `app.py` as the main entrypoint.
4. Click "Deploy". The platform will automatically install packages from `requirements.txt`, load the application, and start the app.

### B. Hugging Face Spaces
1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces) and select **Streamlit** as the SDK.
2. Clone the Hugging Face repository locally or upload the files directly.
3. Make sure to commit the `model_cache/` directory to your Hugging Face Space repository. This ensures that the Space doesn't make any Hugging Face Hub downloads during startup and runs completely offline.
4. Commit and push the files. Hugging Face Spaces will build the container and deploy the app.

---

## 4. Performance & Hardware Benchmarks

* **Total Ranking Pipeline Runtime (100k Candidates)**: **55.26 seconds** (well within the 5-minute wall-clock limit).
  * *Stage 1 Retrieval (100k candidates)*: 23.37 seconds.
  * *Model Loading (Offline cache)*: 0.65 seconds.
  * *Stage 2 Re-ranking & Embedding Encoding (1000 candidates)*: 31.23 seconds.
* **Streamlit Dashboard Load Time**: **< 2 seconds** (after cache generation).
* **Sandbox Candidate Evaluation**: **< 0.05 seconds**.
* **Memory Footprint**: **~142.5 MB RAM** (less than 1% of the 16 GB RAM budget).
* **Network Status**: **0 external API calls** during runtime (100% offline).
