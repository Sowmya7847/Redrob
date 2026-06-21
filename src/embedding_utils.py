import os
from sentence_transformers import SentenceTransformer

def get_embedding_model(model_dir=None, local_files_only=True):
    """
    Loads the all-MiniLM-L6-v2 model.
    Cascade order:
    1. Try loading from model_dir with local_files_only=local_files_only.
    2. Try loading from model_dir without local_files_only restriction.
    3. Auto-download from HF hub, save to cache directory, and return.
    4. Fallback online download of model name directly.
    """
    model_name = "all-MiniLM-L6-v2"
    
    if not model_dir:
        workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_dir = os.path.join(workspace_dir, "model_cache", model_name)
        
    # 1. Try local cache loading first
    try:
        print(f"Attempting to load model from cache: {model_dir}...")
        model = SentenceTransformer(model_dir, device="cpu", local_files_only=local_files_only)
        print("Model loaded successfully from cache.")
        return model
    except Exception as e:
        print(f"Failed to load offline model cache from {model_dir}: {e}")
        
    # 2. Try loading local without local_files_only restriction
    if local_files_only:
        try:
            print("Attempting fallback load without local_files_only restriction...")
            model = SentenceTransformer(model_dir, device="cpu")
            print("Model loaded successfully from cache without restrictions.")
            return model
        except Exception as e2:
            print(f"Fallback cache load failed: {e2}")
            
    # 3. Auto-download and cache
    print(f"Local model not found or failed to load. Auto-downloading {model_name}...")
    old_hf = os.environ.get("HF_HUB_OFFLINE")
    old_tf = os.environ.get("TRANSFORMERS_OFFLINE")
    os.environ["HF_HUB_OFFLINE"] = "0"
    os.environ["TRANSFORMERS_OFFLINE"] = "0"
    
    try:
        os.makedirs(os.path.dirname(model_dir), exist_ok=True)
        model = SentenceTransformer(model_name, device="cpu")
        model.save(model_dir)
        print(f"Model saved successfully to {model_dir}")
        return model
    except Exception as e_dl:
        print(f"Auto-download and caching failed: {e_dl}")
        # 4. Final online fallback
        try:
            print(f"Attempting final fallback online download for {model_name}...")
            model = SentenceTransformer(model_name, device="cpu")
            return model
        except Exception as e_final:
            print(f"Final online fallback failed: {e_final}")
            raise e_final
    finally:
        if old_hf is not None:
            os.environ["HF_HUB_OFFLINE"] = old_hf
        else:
            os.environ["HF_HUB_OFFLINE"] = "1"
        if old_tf is not None:
            os.environ["TRANSFORMERS_OFFLINE"] = old_tf
        else:
            os.environ["TRANSFORMERS_OFFLINE"] = "1"

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
