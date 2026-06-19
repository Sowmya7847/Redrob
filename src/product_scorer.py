import re

# Curated list of known IT Services / Consulting companies
IT_SERVICES_COMPANIES = {
    "infosys", "tcs", "wipro", "accenture", "cognizant", "capgemini", "l&t", 
    "mindtree", "tech mahindra", "mphasis", "hcl", "cts", "tata consultancy services", 
    "cognizant technology solutions", "wipro technologies", "infosys technologies", 
    "hexaware", "persistent systems", "lnt infotech", "ltimindtree"
}

# Curated list of known Product / SaaS / AI companies (including fictional ones)
PRODUCT_COMPANIES = {
    "google", "meta", "microsoft", "amazon", "apple", "netflix", "uber", "ola", 
    "flipkart", "paytm", "swiggy", "zomato", "cred", "razorpay", "hooli", "pied piper", 
    "stark industries", "wayne enterprises", "initech", "globex inc", "globex", "stripe", 
    "salesforce", "atlassian", "canva", "adobe", "nvidia", "openai", "anthropic", 
    "cohere", "hugging face", "snowflake", "databricks", "mongodb", "elastic"
}

# Industries representing product/SaaS/tech platforms
PRODUCT_INDUSTRIES = {
    "software", "internet", "e-commerce", "fintech", "saas", "ai/ml", "artificial intelligence", 
    "adtech", "edtech", "marketplace", "technology", "artificial intelligence & services", 
    "food delivery", "transportation", "conglomerate"
}

# Keywords indicating production engineering, deployments, and scale
PRODUCTION_KEYWORDS = [
    "production", "deploy", "scale", "real user", "serve", "kubernetes", "docker", 
    "aws", "gcp", "azure", "ci/cd", "ndcg", "mrr", "indexing", "latency", "pipeline", 
    "real-time", "streaming", "microservices", "load balancer", "kafka", "redis", 
    "elasticsearch", "optimization", "throughput", "monitoring", "prometheus", "grafana"
]

# Keywords indicating AI/ML product engineering (search, ranking, retrieval, recommendation)
AI_PRODUCT_KEYWORDS = [
    "retrieval", "ranking", "search", "recommendation", "rag", "vector database", 
    "embeddings", "sentence-transformers", "fine-tuning", "llm", "query", "bm25",
    "dense retrieval", "sparse retrieval", "hybrid search", "learning to rank", "cross-encoder"
]

def clean_text(text):
    if not text:
        return ""
    return text.lower().strip()

def is_product_company(company_name, industry_name):
    """
    Classifies a company as Product/SaaS/Tech vs IT Services using rules.
    """
    comp = clean_text(company_name)
    ind = clean_text(industry_name)
    
    # 1. Curated list matches
    if comp in IT_SERVICES_COMPANIES or any(srv in comp for srv in ["infosys", "wipro", "tcs", "accenture", "cognizant", "capgemini"]):
        return False
    if comp in PRODUCT_COMPANIES or any(prd in comp for prd in ["google", "meta", "microsoft", "amazon", "netflix", "uber", "pied piper", "hooli", "wayne", "stark"]):
        return True
        
    # 2. Industry matches
    if any(pi in ind for pi in PRODUCT_INDUSTRIES):
        return True
    if any(si in ind for si in ["it services", "consulting", "outsourcing", "it consulting"]):
        return False
        
    # 3. Company name hints
    if any(hint in comp for hint in ["software", "tech", "ai", "product", "saas", "labs", "systems", "analytics"]):
        return True
        
    # Default fallback: assume it is product if not in consulting
    return True

def compute_product_experience_score(cand):
    """
    Computes the Product Experience Score (0.0 to 1.0) for a candidate.
    """
    career = cand.get("career_history", [])
    if not career:
        return 0.0
        
    total_months = 0
    product_months = 0
    services_only = True
    
    # Track unique keywords found across all jobs
    all_descriptions_text = ""
    
    for job in career:
        comp = job.get("company", "")
        ind = job.get("industry", "")
        dur = job.get("duration_months", 0)
        desc = clean_text(job.get("description", ""))
        
        all_descriptions_text += desc + " "
        total_months += dur
        
        is_prod = is_product_company(comp, ind)
        if is_prod:
            product_months += dur
            services_only = False
            
    # 1. Product Company Ratio (P_company)
    p_company = (product_months / total_months) if total_months > 0 else 0.5
    
    # 2. Production Keywords Score (P_production)
    kw_matches = sum(1 for kw in PRODUCTION_KEYWORDS if kw in all_descriptions_text)
    p_production = min(1.0, kw_matches / 8.0)
    
    # 3. AI Product Fit (P_ai)
    ai_matches = sum(1 for kw in AI_PRODUCT_KEYWORDS if kw in all_descriptions_text)
    p_ai = min(1.0, ai_matches / 4.0)
    
    # Weighted score
    base_score = 0.4 * p_company + 0.4 * p_production + 0.2 * p_ai
    
    # Apply Services Only penalty
    if services_only:
        base_score = max(0.0, base_score - 0.5)
        
    return base_score
