import os
from sentence_transformers import SentenceTransformer

def get_embedding_model(model_dir=None):
    """
    Loads the all-MiniLM-L6-v2 model from a local cache directory to ensure offline execution.
    If the local directory does not exist, it downloads it (runs during development).
    """
    model_name = "all-MiniLM-L6-v2"
    
    # If no directory is specified, use a default folder in the workspace
    if not model_dir:
        workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_dir = os.path.join(workspace_dir, "model_cache", model_name)
        
    if os.path.exists(model_dir):
        # Load offline
        print(f"Loading embedding model offline from {model_dir}...")
        model = SentenceTransformer(model_dir, device="cpu")
    else:
        # Download and cache (development phase only)
        print(f"Local model not found. Downloading {model_name} and caching to {model_dir}...")
        os.makedirs(os.path.dirname(model_dir), exist_ok=True)
        model = SentenceTransformer(model_name, device="cpu")
        model.save(model_dir)
        print(f"Model saved successfully to {model_dir}")
        
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
