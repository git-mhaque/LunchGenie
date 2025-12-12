"""
ReviewAnalyzer: Analyze recent restaurant reviews for red flags using LLM.
Flags issues like food safety, hygiene, or severe service/hospitality problems.
"""

from typing import List, Tuple, Dict
from langchain_openai import ChatOpenAI
from lunchgenie.config import Config

class ReviewAnalyzer:
    def __init__(self, config: Config = None, model_name: str = "gpt-3.5-turbo"):
        self.config = config or Config()
        self.llm = ChatOpenAI(
            openai_api_key=self.config.openai_api_key,
            model_name=model_name,
            temperature=0.15
        )

    def detect_red_flags(self, reviews: List[str]) -> Dict[str, any]:
        """
        Analyzes reviews and returns a dict with findings:
        - 'red_flags': List of flagged review excerpts (if any)
        - 'safe': bool
        - 'summary': 2-3 sentence summary of concerns or OK
        """
        if not reviews:
            return {"red_flags": [], "safe": True, "summary": "No reviews to analyze."}
        # Compose prompt
        review_text = "\n\n".join(f"- {r.strip()}" for r in reviews[:10])  # Up to 10 latest reviews
        prompt = (
            "You are an expert food & safety auditor. Analyze these customer reviews for this restaurant. "
            "Identify and quote any that mention food safety, hygiene, rats/insects, food poisoning, "
            "severe unhygienic conditions, or serious customer mistreatment. "
            "If there are no such issues, reply that it seems safe. "
            "Reply in JSON as {\"red_flags\": ..., \"safe\": ..., \"summary\": ...}\n\n"
            f"Reviews:\n{review_text}"
        )

        response = self.llm.invoke(prompt)
        import json
        try:
            parsed = json.loads(response.content)
            return parsed
        except Exception:
            # Fallback: just include summary and fallback parsing
            return {
                "red_flags": [],
                "safe": False,
                "summary": "LLM response parse error or ambiguous result. Manual review recommended."
            }
