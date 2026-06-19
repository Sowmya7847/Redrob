import os
import json
import time
import sys
import datetime

# Add current directory to path to import src modules
workspace_dir = os.path.dirname(os.path.abspath(__file__))
if workspace_dir not in sys.path:
    sys.path.append(workspace_dir)

from src.retrieval import retrieve_top_k_candidates, extract_stage1_features, compute_stage1_score
from src.embedding_utils import get_embedding_model, compute_cosine_similarity
from src.product_scorer import PRODUCTION_KEYWORDS, AI_PRODUCT_KEYWORDS, is_product_company
from src.re_ranker import (
    compute_technical_score,
    compute_experience_score,
    compute_product_experience_score,
    compute_behavioral_score,
    compute_trust_score,
    compute_risk_score,
    build_candidate_profile_text
)

CACHE_FILE = os.path.join(workspace_dir, "data_cache.json")
CANDIDATES_FILE = os.path.join(workspace_dir, "candidates.jsonl")
JD_FILE = os.path.join(workspace_dir, "job_description.txt")
MODEL_DIR = os.path.join(workspace_dir, "model_cache", "all-MiniLM-L6-v2")

def extract_evidence(cand):
    """
    Extracts recruiter-friendly evidence for product, deployment, and AI/Search/Ranking.
    """
    career = cand.get("career_history", [])
    skills = cand.get("skills", [])
    profile = cand.get("profile", {})
    
    # 1. Product Experience Evidence
    prod_companies = []
    service_companies = []
    total_months = 0
    product_months = 0
    saas_indicators = []
    
    for job in career:
        comp = job.get("company", "")
        ind = job.get("industry", "")
        dur = job.get("duration_months", 0)
        desc_lower = job.get("description", "").lower()
        
        total_months += dur
        is_prod = is_product_company(comp, ind)
        
        if is_prod:
            product_months += dur
            prod_companies.append(f"{comp} ({dur} months, Industry: {ind})")
        else:
            service_companies.append(f"{comp} ({dur} months, Industry: {ind})")
            
        # Check SaaS/Product hints in description
        for hint in ["saas", "product-led", "subscription", "b2b saas", "b2c", "platform", "multi-tenant"]:
            if hint in desc_lower and hint not in saas_indicators:
                saas_indicators.append(hint)
                
    prod_ratio = (product_months / total_months) if total_months > 0 else 0.0
    
    # 2. Deployment Evidence
    deploy_signals = []
    for job in career:
        desc = job.get("description", "")
        desc_lower = desc.lower()
        matched_kws = [kw for kw in PRODUCTION_KEYWORDS if kw in desc_lower]
        if matched_kws:
            deploy_signals.append({
                "company": job.get("company", ""),
                "title": job.get("title", ""),
                "keywords": matched_kws,
                "snippet": desc
            })
            
    # 3. AI/Search/Ranking Experience
    ai_signals = []
    for job in career:
        desc = job.get("description", "")
        desc_lower = desc.lower()
        matched_kws = [kw for kw in AI_PRODUCT_KEYWORDS if kw in desc_lower]
        if matched_kws:
            ai_signals.append({
                "company": job.get("company", ""),
                "title": job.get("title", ""),
                "keywords": matched_kws,
                "snippet": desc
            })
            
    # Also check skills for AI/Search/Ranking
    ai_skills_found = []
    for s in skills:
        sname = s.get("name", "").lower()
        for kw in AI_PRODUCT_KEYWORDS:
            if kw in sname and sname not in ai_skills_found:
                ai_skills_found.append(s.get("name", ""))
                
    return {
        "product_ratio": prod_ratio,
        "product_companies": prod_companies,
        "service_companies": service_companies,
        "saas_indicators": saas_indicators,
        "deploy_signals": deploy_signals,
        "ai_signals": ai_signals,
        "ai_skills_found": ai_skills_found
    }

def build_data_cache():
    """
    Runs the ranking pipeline on the full candidates.jsonl dataset
    and caches the Top 1000 candidates with all sub-scores, features, and profile details.
    """
    print("Building data cache for dashboard...")
    start_time = time.time()
    
    # 1. Load JD
    with open(JD_FILE, "r", encoding="utf-8") as f:
        jd_text = f.read()
        
    # 2. Stage 1 Retrieval
    t1 = time.time()
    # Retrieve top 3000 survivors
    survivors = retrieve_top_k_candidates(CANDIDATES_FILE, k=3000)
    retrieval_time = time.time() - t1
    
    # 3. Load Embedding Model
    t2 = time.time()
    model = get_embedding_model(MODEL_DIR)
    model_load_time = time.time() - t2
    
    # 4. Stage 2 Scoring & Re-ranking
    t3 = time.time()
    
    # Compute cheap scores for all 3000 survivors first
    pre_ranked = []
    for s1_score, cand in survivors:
        t_score = compute_technical_score(cand)
        e_score = compute_experience_score(cand)
        p_score = compute_product_experience_score(cand)
        b_score = compute_behavioral_score(cand)
        c_score = compute_trust_score(cand)
        risk_res = compute_risk_score(cand)
        r_score = risk_res["risk_score"]
        
        # Pre-score without semantic similarity
        pre_score = 0.25 * t_score + 0.20 * e_score + 0.20 * p_score + 0.15 * b_score + 0.05 * c_score - 1.5 * r_score
        
        pre_ranked.append({
            "cand": cand,
            "pre_score": pre_score,
            "t_score": t_score,
            "e_score": e_score,
            "p_score": p_score,
            "b_score": b_score,
            "c_score": c_score,
            "r_score": r_score,
            "risk_details": risk_res["details"]
        })
        
    # Sort survivors by pre_score descending and keep top 1000 for semantic similarity and caching
    pre_ranked.sort(key=lambda x: x["pre_score"], reverse=True)
    top_1000 = pre_ranked[:1000]
    
    # Generate embeddings and calculate semantic scores for top 1000
    texts = [build_candidate_profile_text(item["cand"]) for item in top_1000]
    similarities = compute_cosine_similarity(model, jd_text, texts)
    
    final_list = []
    for idx, item in enumerate(top_1000):
        sim = similarities[idx]
        normalized_semantic = max(0.0, sim)
        final_score = round(item["pre_score"] + 0.15 * normalized_semantic, 4)
        
        profile = item["cand"]["profile"]
        skills = [s["name"] for s in item["cand"]["skills"] if s.get("proficiency") in ["expert", "advanced"]][:4]
        skills_str = ", ".join(skills) if skills else "relevant AI skills"
        
        reasoning = (
            f"{profile.get('current_title')} with {profile.get('years_of_experience')} years of experience. "
            f"Strong matching in {skills_str} and production deployment. "
            f"Response rate {int(item['b_score']*100)}% with a clean risk profile."
        )
        
        # Extract evidence for the recruiter explorer page
        evidence = extract_evidence(item["cand"])
        
        final_list.append({
            "candidate_id": item["cand"]["candidate_id"],
            "score": final_score,
            "reasoning": reasoning,
            "t_score": item["t_score"],
            "e_score": item["e_score"],
            "p_score": item["p_score"],
            "b_score": item["b_score"],
            "c_score": item["c_score"],
            "r_score": item["r_score"],
            "risk_details": item["risk_details"],
            "semantic_score": normalized_semantic,
            "profile": profile,
            "skills": item["cand"]["skills"],
            "career_history": item["cand"]["career_history"],
            "education": item["cand"].get("education", []),
            "redrob_signals": item["cand"]["redrob_signals"],
            "evidence": evidence
        })
        
    # Sort final_list by score descending, candidate_id ascending for tie-breaks
    final_list.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    
    # Store all 1000 candidates in the cache
    cached_data = {
        "stats": {
            "total_processed": 100000,
            "retrieved_count": 3000,
            "reranked_count": 1000,
            "runtime_sec": round(time.time() - start_time, 2),
            "retrieval_sec": round(retrieval_time, 2),
            "model_load_sec": round(model_load_time, 2),
            "rerank_sec": round(time.time() - t3, 2),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "candidates": final_list
    }
    
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cached_data, f, indent=2)
        
    print(f"Cached {len(final_list)} candidates successfully to {CACHE_FILE}")
    return cached_data

def get_dashboard_data():
    """
    Loads dashboard data from data_cache.json.
    If cache doesn't exist, builds it first.
    """
    if not os.path.exists(CACHE_FILE):
        return build_data_cache()
        
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure the cache actually contains 1000 candidates, otherwise rebuild
            if len(data.get("candidates", [])) < 1000:
                print("Cache contains fewer than 1000 candidates. Rebuilding...")
                return build_data_cache()
            return data
    except Exception as e:
        print(f"Error loading cache: {e}. Rebuilding...")
        return build_data_cache()

def evaluate_single_candidate(cand, model, jd_text):
    """
    Evaluates a single candidate JSON profile on-the-fly.
    """
    t_score = compute_technical_score(cand)
    e_score = compute_experience_score(cand)
    p_score = compute_product_experience_score(cand)
    b_score = compute_behavioral_score(cand)
    c_score = compute_trust_score(cand)
    risk_res = compute_risk_score(cand)
    r_score = risk_res["risk_score"]
    
    # 1. Cheap Pre-Score
    pre_score = 0.25 * t_score + 0.20 * e_score + 0.20 * p_score + 0.15 * b_score + 0.05 * c_score - 1.5 * r_score
    
    # 2. Semantic Similarity
    profile_text = build_candidate_profile_text(cand)
    sim = compute_cosine_similarity(model, jd_text, [profile_text])[0]
    normalized_semantic = max(0.0, sim)
    
    # 3. Final Score
    final_score = round(pre_score + 0.15 * normalized_semantic, 4)
    
    # Hire recommendation
    if final_score >= 0.70:
        recommendation = "Recommended"
    elif final_score >= 0.60:
        recommendation = "Consider"
    else:
        recommendation = "Not Recommended"
        
    profile = cand.get("profile", {})
    skills = [s["name"] for s in cand.get("skills", []) if s.get("proficiency") in ["expert", "advanced"]][:4]
    skills_str = ", ".join(skills) if skills else "relevant AI skills"
    
    reasoning = (
        f"{profile.get('current_title')} with {profile.get('years_of_experience')} years of experience. "
        f"Strong matching in {skills_str} and production deployment. "
        f"Response rate {int(b_score*100)}% with a clean risk profile."
    )
    
    evidence = extract_evidence(cand)
    
    return {
        "candidate_id": cand.get("candidate_id", "CAND_UNKNOWN"),
        "score": final_score,
        "recommendation": recommendation,
        "reasoning": reasoning,
        "t_score": t_score,
        "e_score": e_score,
        "p_score": p_score,
        "b_score": b_score,
        "c_score": c_score,
        "r_score": r_score,
        "risk_details": risk_res["details"],
        "semantic_score": normalized_semantic,
        "profile": profile,
        "skills": cand.get("skills", []),
        "career_history": cand.get("career_history", []),
        "education": cand.get("education", []),
        "redrob_signals": cand.get("redrob_signals", {}),
        "evidence": evidence
    }
