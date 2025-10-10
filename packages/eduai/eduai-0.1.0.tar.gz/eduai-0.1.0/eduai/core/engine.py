"""
Core engine for EduAI
Provides a simple API: EduAI.summarize, generate_quiz, explain
Uses a pluggable model adapter (fallback by default).
"""

from typing import List, Dict, Optional
from ..models.fallback_model import FallbackModel

class EduAI:
    def __init__(self, model_name: str = "fallback", model_adapter=None):
        """
        model_name: "fallback" | "openai" | "gemini"
        model_adapter: optional custom adapter instance implementing .summarize/.quiz/.explain
        """
        if model_adapter is not None:
            self.model = model_adapter
        else:
            # choose adapter by name (only fallback included by default)
            if model_name == "fallback":
                self.model = FallbackModel()
            else:
                # keep fallback as default if unknown
                self.model = FallbackModel()

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        return self.model.summarize(text, max_sentences=max_sentences)

    def generate_quiz(self, text: str, num_questions: int = 3) -> List[Dict]:
        return self.model.generate_quiz(text, num_questions=num_questions)

    def explain(self, text: str, level: str = "child") -> str:
        return self.model.explain(text, level=level)
