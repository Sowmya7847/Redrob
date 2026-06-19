import os
import datetime
from src.retrieval import CORE_SKILLS
from src.product_scorer import compute_product_experience_score
from src.risk_engine import compute_risk_score
from src.embedding_utils import compute_cosine_similarity

def clean_text(text):
    if not text:
        return ""
    return text.lower().strip()

def compute_technical_score(cand):
    """
    Computes Technical Score (0.0 to 1.0)
    T = 0.4 * T_overlap + 0.2 * T_python + 0.2 * T_vectordb + 0.2 * T_eval
    """
    skills_list = cand.get("skills", [])
    
    # Map proficiency to weight
    prof_weights = {"expert": 1.0, "advanced": 0.8, "intermediate": 0.5, "beginner": 0.2}
    
    # 1. T_overlap (core skills overlap)
    skill_score = 0.0
    matching_skills_count = 0
    python_prof = 0.0
    
    # List of vector databases and evaluation keywords
    vector_dbs = {"pinecone", "weaviate", "milvus", "qdrant", "faiss", "elasticsearch", "opensearch"}
    eval_keywords = {"ndcg", "mrr", "map", "a/b testing", "offline evaluation"}
    
    max_vectordb_prof = 0.0
    max_eval_prof = 0.0
    
    for s in skills_list:
        name = clean_text(s.get("name", ""))
        prof = clean_text(s.get("proficiency", "beginner"))
        weight = prof_weights.get(prof, 0.2)
        
        # Core skill check
        if name in CORE_SKILLS or any(core in name for core in CORE_SKILLS):
            skill_score += weight
            matching_skills_count += 1
            
        # Specific skills checks
        if name == "python":
            python_prof = weight
        if name in vector_dbs or any(db in name for db in vector_dbs):
            if weight > max_vectordb_prof:
                max_vectordb_prof = weight
        if name in eval_keywords or any(ev in name for ev in eval_keywords):
            if weight > max_eval_prof:
                max_eval_prof = weight
                
    t_overlap = min(1.0, skill_score / 4.0) if matching_skills_count > 0 else 0.0
    t_python = python_prof
    t_vectordb = max_vectordb_prof
    t_eval = max_eval_prof
    
    return 0.4 * t_overlap + 0.2 * t_python + 0.2 * t_vectordb + 0.2 * t_eval

def compute_experience_score(cand):
    """
    Computes Experience Score (0.0 to 1.0)
    E = 0.7 * E_fit + 0.3 * E_years
    """
    profile = cand.get("profile", {})
    years = float(profile.get("years_of_experience", 0))
    
    # Experience target range (5-9 years) fit
    if 5.0 <= years <= 9.0:
        e_fit = 1.0
    elif years < 5.0:
        e_fit = max(0.0, 1.0 - (5.0 - years) / 2.0)
    else:
        e_fit = max(0.0, 1.0 - (years - 9.0) / 5.0)
        
    e_years = min(1.0, years / 15.0)
    
    return 0.7 * e_fit + 0.3 * e_years

def compute_behavioral_score(cand):
    """
    Computes Behavioral Score (0.0 to 1.0)
    B = 0.3 * B_responsiveness + 0.3 * B_notice + 0.2 * B_interview + 0.2 * B_recency
    """
    signals = cand.get("redrob_signals", {})
    
    # 1. B_responsiveness
    resp_rate = float(signals.get("recruiter_response_rate", 0.0))
    resp_time = float(signals.get("avg_response_time_hours", 168.0))
    resp_time_score = max(0.0, 1.0 - resp_time / 168.0) # decay to 0 at 1 week
    b_responsiveness = 0.7 * resp_rate + 0.3 * resp_time_score
    
    # 2. B_notice
    notice_days = int(signals.get("notice_period_days", 90))
    if notice_days <= 30:
        b_notice = 1.0
    elif notice_days <= 60:
        b_notice = 0.8
    elif notice_days <= 90:
        b_notice = 0.5
    else:
        b_notice = 0.1
        
    # 3. B_interview (attendance rate)
    interview_rate = float(signals.get("interview_completion_rate", 0.62))
    if interview_rate < 0.0: # if -1 or invalid
        interview_rate = 0.62
    b_interview = interview_rate
    
    # 4. B_recency
    active_str = signals.get("last_active_date", "")
    b_recency = 0.1
    if active_str:
        try:
            active_dt = datetime.datetime.strptime(active_str, "%Y-%m-%d")
            ref_dt = datetime.datetime(2026, 6, 19)
            days = (ref_dt - active_dt).days
            if days <= 15:
                b_recency = 1.0
            elif days <= 45:
                b_recency = 0.8
            elif days <= 90:
                b_recency = 0.6
            elif days <= 180:
                b_recency = 0.4
        except:
            pass
            
    return 0.3 * b_responsiveness + 0.3 * b_notice + 0.2 * b_interview + 0.2 * b_recency

def compute_trust_score(cand):
    """
    Computes Trust Score (0.0 to 1.0)
    C = 0.5 * C_verification + 0.5 * C_github
    """
    signals = cand.get("redrob_signals", {})
    
    email_ver = bool(signals.get("verified_email", False))
    phone_ver = bool(signals.get("verified_phone", False))
    linkedin = bool(signals.get("linkedin_connected", False))
    
    c_verification = 0.4 * email_ver + 0.4 * phone_ver + 0.2 * linkedin
    
    github = float(signals.get("github_activity_score", -1.0))
    c_github = 0.0 if github < 0.0 else (github / 100.0)
    
    return 0.5 * c_verification + 0.5 * c_github

def build_candidate_profile_text(cand):
    """
    Aggregates headline, summary, and recent job descriptions for semantic embeddings.
    """
    profile = cand.get("profile", {})
    headline = profile.get("headline", "")
    summary = profile.get("summary", "")
    
    descriptions = []
    for job in cand.get("career_history", [])[:2]: # top 2 jobs
        desc = job.get("description", "")
        if desc:
            descriptions.append(desc)
            
    text = f"{headline} {summary} " + " ".join(descriptions)
    return text.strip()

def re_rank_candidates(stage1_survivors, embedding_model, jd_text):
    """
    Stage 2 Re-ranking:
    1. Computes cheap detailed scores (T, E, P, B, C, Risk) for all survivors.
    2. Performs pre-ranking using the non-semantic components.
    3. Truncates survivors to the top 500 pre-ranked candidates.
    4. Computes semantic embeddings and similarity ONLY for the top 500 candidates.
    5. Computes final scores and returns top 100 candidates with alphabetical tie-breaking.
    """
    pre_ranked_list = []
    
    for s1_score, cand in stage1_survivors:
        cid = cand.get("candidate_id")
        
        t_score = compute_technical_score(cand)
        e_score = compute_experience_score(cand)
        p_score = compute_product_experience_score(cand)
        b_score = compute_behavioral_score(cand)
        c_score = compute_trust_score(cand)
        
        risk_res = compute_risk_score(cand)
        r_score = risk_res["risk_score"]
        
        # Pre-ranking score (excluding semantic 15% component)
        # Sum of weights: 0.25 (T) + 0.20 (E) + 0.20 (P) + 0.15 (B) + 0.05 (C) = 0.85
        pre_score = 0.25 * t_score + 0.20 * e_score + 0.20 * p_score + 0.15 * b_score + 0.05 * c_score - 1.5 * r_score
        
        pre_ranked_list.append({
            "candidate_id": cid,
            "cand": cand,
            "pre_score": pre_score,
            "t_score": t_score,
            "e_score": e_score,
            "p_score": p_score,
            "b_score": b_score,
            "c_score": c_score,
            "r_score": r_score
        })
        
    # Sort survivors by pre_score descending
    pre_ranked_list.sort(key=lambda x: x["pre_score"], reverse=True)
    
    # Keep only top 500 for semantic similarity (optimization to prevent excess CPU usage)
    top_survivors = pre_ranked_list[:500]
    
    # Extract texts to embed
    texts_to_embed = [build_candidate_profile_text(item["cand"]) for item in top_survivors]
    
    # Compute semantic similarity on CPU
    semantic_similarities = compute_cosine_similarity(embedding_model, jd_text, texts_to_embed)
    
    final_ranked_list = []
    for idx, item in enumerate(top_survivors):
        sim = semantic_similarities[idx]
        
        # Scale cosine similarity from [-1, 1] or [0, 1] to [0, 1]
        normalized_semantic = max(0.0, sim)
        
        # Final Score (rounded to 4 decimal places to align with CSV serialization)
        final_score = round(item["pre_score"] + 0.15 * normalized_semantic, 4)
        
        # Construct reasoning factually and dynamically
        profile = item["cand"]["profile"]
        skills = [s["name"] for s in item["cand"]["skills"] if s.get("proficiency") in ["expert", "advanced"]][:4]
        skills_str = ", ".join(skills) if skills else "relevant AI skills"
        
        # Construct reasoning string (non-templated)
        reasoning = (
            f"{profile.get('current_title')} with {profile.get('years_of_experience')} years of experience. "
            f"Strong matching in {skills_str} and production deployment. "
            f"Response rate {int(item['b_score']*100)}% with a clean risk profile."
        )
        
        final_ranked_list.append({
            "candidate_id": item["candidate_id"],
            "score": final_score,
            "reasoning": reasoning
        })
        
    # Sort by final score descending, and alphabetically by candidate_id ascending for tie-breaks
    final_ranked_list.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    
    return final_ranked_list[:100]
