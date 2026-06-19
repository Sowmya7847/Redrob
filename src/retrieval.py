import json
import heapq
import os

# Curated core skills list for Stage 1 retrieval
CORE_SKILLS = {
    "embeddings", "retrieval", "vector database", "vector search", "hybrid search",
    "python", "ndcg", "mrr", "map", "a/b testing", "nlp", "information retrieval",
    "pinecone", "weaviate", "milvus", "qdrant", "faiss", "elasticsearch", "opensearch",
    "sentence-transformers", "peft", "lora", "qlora", "fine-tuning", "xgboost",
    "learning to rank", "ltr", "reranking", "rerank", "search engine", "recommendation"
}

# Core keywords for Stage 1 relevance checking
RELEVANCE_KEYWORDS = [
    "retrieval", "ranking", "search", "recommendation", "vector", "embedding",
    "nlp", "llm", "ir", "rag", "production", "scale", "deploy", "pipeline",
    "weaviate", "pinecone", "milvus", "qdrant", "faiss", "sentence-transformers"
]

def clean_text(text):
    if not text:
        return ""
    return text.lower().strip()

def extract_stage1_features(cand):
    """
    Extracts cheap features for Stage 1 filtering and retrieval.
    """
    profile = cand.get("profile", {})
    skills_list = cand.get("skills", [])
    
    # 1. Experience
    years = float(profile.get("years_of_experience", 0))
    
    # 2. Location & Country
    location = clean_text(profile.get("location", ""))
    country = clean_text(profile.get("country", ""))
    willing_to_relocate = bool(cand.get("redrob_signals", {}).get("willing_to_relocate", False))
    
    # 3. Skills
    candidate_skills = {}
    for s in skills_list:
        name = clean_text(s.get("name", ""))
        proficiency = clean_text(s.get("proficiency", "beginner"))
        candidate_skills[name] = proficiency
        
    # 4. Titles (Current & History)
    current_title = clean_text(profile.get("current_title", ""))
    past_titles = []
    for job in cand.get("career_history", []):
        t = clean_text(job.get("title", ""))
        if t:
            past_titles.append(t)
            
    # 5. Text content for keyword matching (Headline + Summary + Recent Job Description)
    text_content = clean_text(profile.get("headline", "")) + " " + clean_text(profile.get("summary", ""))
    if cand.get("career_history"):
        text_content += " " + clean_text(cand["career_history"][0].get("description", ""))
        
    # 6. Responsiveness & notice period
    responsiveness = float(cand.get("redrob_signals", {}).get("recruiter_response_rate", 0.0))
    profile_completeness = float(cand.get("redrob_signals", {}).get("profile_completeness_score", 0.0)) / 100.0
    notice_days = int(cand.get("redrob_signals", {}).get("notice_period_days", 90))
    
    return {
        "candidate_id": cand.get("candidate_id"),
        "years": years,
        "location": location,
        "country": country,
        "willing_to_relocate": willing_to_relocate,
        "skills": candidate_skills,
        "current_title": current_title,
        "past_titles": past_titles,
        "text_content": text_content,
        "responsiveness": responsiveness,
        "profile_completeness": profile_completeness,
        "notice_days": notice_days
    }

def compute_stage1_score(feat):
    """
    Computes a broad retrieval score for Stage 1 re-ranking.
    Returns a score between 0.0 and 1.5+ (including location boosting).
    """
    # 1. Skill Overlap (weighted by proficiency)
    skill_score = 0.0
    matching_skills_count = 0
    prof_weights = {"expert": 1.0, "advanced": 0.8, "intermediate": 0.5, "beginner": 0.2}
    for sk, prof in feat["skills"].items():
        if sk in CORE_SKILLS or any(core in sk for core in CORE_SKILLS):
            skill_score += prof_weights.get(prof, 0.2)
            matching_skills_count += 1
            
    skill_overlap = min(1.0, skill_score / 4.0) if matching_skills_count > 0 else 0.0
    
    # 2. Title Relevance
    title_relevance = 0.1
    all_titles = [feat["current_title"]] + feat["past_titles"]
    
    # Check current title first (highest weight)
    curr = feat["current_title"]
    if any(k in curr for k in ["ai engineer", "machine learning engineer", "ml engineer", "nlp engineer", "search engineer", "retrieval engineer", "ranking engineer"]):
        title_relevance = 1.0
    elif any(k in curr for k in ["data scientist", "applied scientist"]):
        title_relevance = 0.8
    elif any(k in curr for k in ["software engineer", "backend engineer", "data engineer", "full stack developer", "cloud engineer"]):
        title_relevance = 0.6
    else:
        # Check if past titles have ML/AI keywords
        has_past_ml = False
        for pt in feat["past_titles"]:
            if any(k in pt for k in ["ml", "machine learning", "ai", "nlp", "search", "retrieval", "ranking", "data scientist"]):
                has_past_ml = True
                break
        if has_past_ml:
            title_relevance = 0.4
            
    # 3. Keyword Relevance
    text = feat["text_content"]
    kw_matches = sum(1 for kw in RELEVANCE_KEYWORDS if kw in text)
    keyword_relevance = min(1.0, kw_matches / 8.0)
    
    # 4. Experience Fit (Target 5-9 years)
    years = feat["years"]
    if 5.0 <= years <= 9.0:
        experience_fit = 1.0
    elif years < 5.0:
        experience_fit = max(0.0, 1.0 - (5.0 - years) / 2.5)  # 2.5 years experience -> 0.0 score
    else:
        experience_fit = max(0.0, 1.0 - (years - 9.0) / 6.0)  # 15 years experience -> 0.0 score
        
    # Combine Stage 1 Score
    stage1_base = (
        0.35 * skill_overlap +
        0.30 * title_relevance +
        0.15 * keyword_relevance +
        0.20 * experience_fit
    )
    
    # 5. Location and Country Boosting (Prefer boosting to exclusion)
    loc_multiplier = 1.0
    
    # Country check: If outside India, apply a de-boosting penalty (0.3x)
    if feat["country"] != "india":
        loc_multiplier *= 0.3
        
    # City matching
    is_pune_noida = any(city in feat["location"] for city in ["pune", "noida"])
    is_other_target = any(city in feat["location"] for city in ["delhi", "ncr", "mumbai", "hyderabad", "bangalore", "chennai"])
    
    if is_pune_noida:
        loc_multiplier *= 1.25  # 25% boost for target hubs
    elif is_other_target or feat["willing_to_relocate"]:
        loc_multiplier *= 1.10  # 10% boost for tier-1 cities or relocation-willing candidates
        
    return stage1_base * loc_multiplier

def retrieve_top_k_candidates(candidates_path, k=3000):
    """
    Streams candidates from JSONL and retrieves top K matches based on Stage 1 Retrieval Score.
    Uses a min-heap to operate in O(N log K) time and O(K) memory.
    """
    heap = []
    
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            cand = json.loads(line)
            feat = extract_stage1_features(cand)
            score = compute_stage1_score(feat)
            
            # Use candidate_id as tie-breaker in heap (smaller ID pushed first)
            entry = (score, feat["candidate_id"], cand)
            
            if len(heap) < k:
                heapq.heappush(heap, entry)
            else:
                # Compare against the smallest score in heap
                if score > heap[0][0]:
                    heapq.heappushpop(heap, entry)
                    
    # Sort the final candidates descending by score
    retrieved = []
    while heap:
        score, cid, cand = heapq.heappop(heap)
        retrieved.append((score, cand))
        
    retrieved.reverse() # Sort descending
    return retrieved
