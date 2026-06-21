import os
from sentence_transformers import SentenceTransformer

def get_embedding_model(model_dir=None, local_files_only=True):
    """
    Loads the all-MiniLM-L6-v2 model.
    If local_files_only=True, it loads strictly from the cache using local_files_only=True.
    If local_files_only=False, it downloads and caches the model.
    """
    model_name = "all-MiniLM-L6-v2"
    
    # If no directory is specified, use a default folder in the workspace
    if not model_dir:
        workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_dir = os.path.join(workspace_dir, "model_cache", model_name)
        
    if local_files_only:
        # Load offline strictly per instruction
        print(f"Loading embedding model offline from {model_dir}...")
        model = SentenceTransformer(model_dir, device="cpu", local_files_only=True)
    else:
        # Download and cache (offline mode disabled temporarily)
        print(f"Downloading model {model_name} and caching to {model_dir}...")
        os.makedirs(os.path.dirname(model_dir), exist_ok=True)
        
        old_hf = os.environ.get("HF_HUB_OFFLINE")
        old_tf = os.environ.get("TRANSFORMERS_OFFLINE")
        os.environ["HF_HUB_OFFLINE"] = "0"
        os.environ["TRANSFORMERS_OFFLINE"] = "0"
        
        try:
            model = SentenceTransformer(model_name, device="cpu")
            model.save(model_dir)
            print(f"Model saved successfully to {model_dir}")
            # Verify integrity
            verify_model = SentenceTransformer(model_dir, device="cpu", local_files_only=True)
            print("Model cache integrity verified successfully.")
            model = verify_model
        finally:
            if old_hf is not None:
                os.environ["HF_HUB_OFFLINE"] = old_hf
            else:
                os.environ["HF_HUB_OFFLINE"] = "1"
            if old_tf is not None:
                os.environ["TRANSFORMERS_OFFLINE"] = old_tf
            else:
                os.environ["TRANSFORMERS_OFFLINE"] = "1"
        
    return model

def compute_cosine_similarity(model, jd_text, candidate_texts):
    """
    Computes cosine similarity between a single Job Description text and a list of candidate texts.
    Returns a list of float similarity scores.
    """
    if not candidate_texts:
        return []
        
    # Encode JD and candidates
    jd_embedding = model.encode(jd_text, convert_to_tensor=True, show_progress_bar=False)
    cand_embeddings = model.encode(candidate_texts, convert_to_tensor=True, show_progress_bar=False)
    
    # Compute similarities
    from sentence_transformers import util
    similarities = util.cos_sim(jd_embedding, cand_embeddings)[0].tolist()
    return similarities
