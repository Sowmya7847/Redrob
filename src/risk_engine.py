import datetime

def clean_text(text):
    if not text:
        return ""
    return text.lower().strip()

def compute_risk_score(cand):
    """
    Computes a continuous RiskScore between 0.0 and 1.0 based on 4 weighted sub-components:
    RiskScore = 0.35 * DurationRisk + 0.30 * ExperienceRisk + 0.20 * SkillInflationRisk + 0.15 * TimelineRisk
    """
    profile = cand.get("profile", {})
    career = cand.get("career_history", [])
    skills = cand.get("skills", [])
    education = cand.get("education", [])
    
    max_ref_date = datetime.datetime(2026, 6, 19) # current date reference
    
    # 1. Duration Risk (R_dur)
    max_mismatch = 0
    for job in career:
        start_str = job.get("start_date")
        end_str = job.get("end_date")
        dur = job.get("duration_months", 0)
        
        if start_str:
            try:
                start_dt = datetime.datetime.strptime(start_str, "%Y-%m-%d")
                if end_str:
                    end_dt = datetime.datetime.strptime(end_str, "%Y-%m-%d")
                else:
                    end_dt = max_ref_date
                
                calendar_months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
                mismatch = max(0, dur - calendar_months)
                if mismatch > max_mismatch:
                    max_mismatch = mismatch
            except:
                pass
                
    if max_mismatch > 12:
        r_dur = min(1.0, max_mismatch / 120.0)
    else:
        r_dur = 0.0
        
    # 2. Experience Risk (R_exp)
    years_of_experience = float(profile.get("years_of_experience", 0))
    sum_career_months = sum(job.get("duration_months", 0) for job in career)
    sum_career_years = sum_career_months / 12.0
    
    diff_years = abs(years_of_experience - sum_career_years)
    if diff_years > 5.0:
        r_exp = min(1.0, diff_years / 15.0)
    else:
        r_exp = 0.0
        
    # 3. Skill Inflation Risk (R_skill)
    inflated_count = 0
    total_skills = len(skills)
    
    for s in skills:
        prof = clean_text(s.get("proficiency", ""))
        dur = s.get("duration_months", 0)
        if prof in ["expert", "advanced"] and dur == 0:
            inflated_count += 1
            
    if total_skills > 0 and inflated_count > 0:
        # Scale: 5 inflated skills in 15 total skills -> ratio = 0.33 -> 0.33 * 5 = 1.65 (capped at 1.0)
        r_skill = min(1.0, (inflated_count / total_skills) * 5.0)
    else:
        r_skill = 0.0
        
    # 4. Timeline Risk (R_time)
    r_time = 0.0
    if education and career:
        edu_starts = [ed.get("start_year") for ed in education if ed.get("start_year")]
        if edu_starts:
            min_edu_start = min(edu_starts)
            
            career_years = []
            for job in career:
                start_str = job.get("start_date")
                if start_str:
                    try:
                        start_year = int(start_str.split('-')[0])
                        career_years.append(start_year)
                    except:
                        pass
                        
            if career_years:
                min_career_start = min(career_years)
                gap = min_edu_start - min_career_start
                if gap >= 6:
                    # Gap of 6 -> (6-5)/3 = 0.33 risk. Gap of 8 -> (8-5)/3 = 1.0 risk.
                    r_time = min(1.0, (gap - 5) / 3.0)
                    
    # Weighted aggregation
    risk_score = 0.35 * r_dur + 0.30 * r_exp + 0.20 * r_skill + 0.15 * r_time
    
    return {
        "risk_score": risk_score,
        "details": {
            "r_dur": r_dur,
            "r_exp": r_exp,
            "r_skill": r_skill,
            "r_time": r_time
        }
    }
