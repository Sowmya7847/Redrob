import unittest
import os
import sys

# Add current directory to path
workspace_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(workspace_dir)

from src.retrieval import compute_stage1_score, extract_stage1_features
from src.product_scorer import is_product_company, compute_product_experience_score
from src.risk_engine import compute_risk_score
from src.re_ranker import (
    compute_technical_score,
    compute_experience_score,
    compute_behavioral_score,
    compute_trust_score
)

class TestRetrievalEngine(unittest.TestCase):
    def test_location_boosting_pune_noida(self):
        # Pune gets a 1.25 de-facto boost
        feat = {
            "country": "india",
            "location": "pune",
            "willing_to_relocate": False,
            "skills": {},
            "current_title": "senior ai engineer",
            "past_titles": [],
            "text_content": "",
            "years": 7.0
        }
        score = compute_stage1_score(feat)
        # Verify the location multiplier boosts the base title relevance (1.0 * 0.30 = 0.30 base + 0.20 exp = 0.50 base)
        # 0.50 base * 1.25 = 0.625
        self.assertAlmostEqual(score, 0.625)

    def test_country_deboosting(self):
        # Candidates outside India get a 0.3x multiplier de-boost
        feat = {
            "country": "united states",
            "location": "san francisco",
            "willing_to_relocate": False,
            "skills": {},
            "current_title": "senior ai engineer",
            "past_titles": [],
            "text_content": "",
            "years": 7.0
        }
        score = compute_stage1_score(feat)
        # Base: (0.30 title + 0.20 exp) = 0.50 base
        # 0.50 base * 0.3 = 0.150
        self.assertAlmostEqual(score, 0.150)

class TestProductScorer(unittest.TestCase):
    def test_company_classification(self):
        # Verify product vs service classification
        self.assertTrue(is_product_company("Google", "Technology"))
        self.assertFalse(is_product_company("Infosys", "IT Consulting"))
        self.assertTrue(is_product_company("Pied Piper", "Software"))
        self.assertFalse(is_product_company("TCS", "Consulting"))

    def test_services_only_penalty(self):
        # Candidates with services-only profiles get a 0.5 penalty
        cand = {
            "career_history": [
                {"company": "Infosys", "industry": "IT Consulting", "duration_months": 24, "description": ""},
                {"company": "Wipro", "industry": "IT Consulting", "duration_months": 24, "description": ""}
            ]
        }
        score = compute_product_experience_score(cand)
        # Product company ratio is 0.0. Penalty is -0.5, capped at 0.0
        self.assertEqual(score, 0.0)

class TestRiskEngine(unittest.TestCase):
    def test_timeline_gap_risk(self):
        # Career starts in 2012, College starts in 2020 -> gap = 2020 - 2012 = 8 years gap
        cand = {
            "profile": {"years_of_experience": 5.0},
            "career_history": [
                {"start_date": "2012-01-01", "duration_months": 60, "company": "A", "description": ""}
            ],
            "skills": [],
            "education": [
                {"start_year": 2020}
            ]
        }
        res = compute_risk_score(cand)
        self.assertAlmostEqual(res["details"]["r_time"], 1.0)
        # Risk score is 0.15 * r_time = 0.15
        self.assertAlmostEqual(res["risk_score"], 0.15)

    def test_clean_profile_no_risk(self):
        cand = {
            "profile": {"years_of_experience": 4.0},
            "career_history": [
                {"start_date": "2022-01-01", "duration_months": 48, "company": "A", "description": ""}
            ],
            "skills": [],
            "education": [
                {"start_year": 2018} # 4 years gap is below the 5-year threshold
            ]
        }
        res = compute_risk_score(cand)
        self.assertEqual(res["risk_score"], 0.0)

class TestReRanker(unittest.TestCase):
    def test_technical_score_calculation(self):
        # Test skills overlap weighting
        cand = {
            "skills": [
                {"name": "Python", "proficiency": "expert"},
                {"name": "Pinecone", "proficiency": "expert"},
                {"name": "ndcg", "proficiency": "expert"}
            ]
        }
        score = compute_technical_score(cand)
        # Expert python: 1.0 -> 0.2 score contribution
        # Expert Pinecone: 1.0 -> 0.2 vector DB contribution
        # Expert NDCG: 1.0 -> 0.2 evaluation contribution
        # Skill overlap: 3 matching core skills -> 3.0 / 4 = 0.75 -> 0.4 * 0.75 = 0.3 score contribution
        # Total Technical Score: 0.3 + 0.2 + 0.2 + 0.2 = 0.90
        self.assertAlmostEqual(score, 0.90)

    def test_experience_score_target_fit(self):
        cand = {
            "profile": {"years_of_experience": 7.0} # targets 5-9 range
        }
        score = compute_experience_score(cand)
        # 7 years experience fits target range -> E_fit = 1.0
        # E_years = 7.0 / 15.0 = 0.4667
        # Total: 0.7 * 1.0 + 0.3 * (7/15) = 0.7 + 0.14 = 0.840
        self.assertAlmostEqual(score, 0.840)

    def test_behavioral_score_responsiveness(self):
        cand = {
            "redrob_signals": {
                "recruiter_response_rate": 0.80,
                "avg_response_time_hours": 24, # 24 hrs -> 1 - 24/168 = 0.857
                "notice_period_days": 30, # <= 30 days -> notice_score = 1.0
                "interview_completion_rate": 0.90, # rate = 0.90
                "last_active_date": "2026-06-18" # active within 15 days -> active_score = 1.0
            }
        }
        score = compute_behavioral_score(cand)
        # Responsiveness component: 0.7 * 0.8 + 0.3 * (1 - 24/168) = 0.56 + 0.257 = 0.817
        # Notice: 1.0
        # Interview: 0.9
        # Recency: 1.0
        # Behavioral score: 0.3 * 0.817 + 0.3 * 1.0 + 0.2 * 0.9 + 0.2 * 1.0 = 0.245 + 0.3 + 0.18 + 0.2 = 0.925
        self.assertTrue(score > 0.90)

    def test_trust_score(self):
        cand = {
            "redrob_signals": {
                "verified_email": True,
                "verified_phone": True,
                "linkedin_connected": True,
                "github_activity_score": 80
            }
        }
        score = compute_trust_score(cand)
        # Verification score: 0.4*1 + 0.4*1 + 0.2*1 = 1.0
        # Github: 80 / 100 = 0.8
        # Combined Trust Score: 0.5 * 1.0 + 0.5 * 0.8 = 0.90
        self.assertAlmostEqual(score, 0.90)

def run_all_tests():
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n==================================================")
    print("   TEST SUITE EXECUTION SUMMARY")
    print("==================================================")
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("==================================================")
    
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
