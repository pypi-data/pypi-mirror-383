"""
Template adapter for Google Gemini - configure and implement calls if you want live Gemini support.
This file is intentionally a template.
"""

import os

class GeminiModel:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise RuntimeError("GOOGLE_API_KEY not found in environment - set it to enable Gemini adapter.")

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        raise NotImplementedError("Gemini adapter not implemented (template).")

    def generate_quiz(self, text: str, num_questions: int = 3):
        raise NotImplementedError("Gemini adapter not implemented (template).")

    def explain(self, text: str, level: str = "child"):
        raise NotImplementedError("Gemini adapter not implemented in this template.")
