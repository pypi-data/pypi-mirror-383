"""
Template adapter for OpenAI - configure and implement calls if you want live GPT support.
This file is intentionally a template and will not be executed unless you
install `openai` and provide an API key.
"""

import os

class OpenAIModel:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not found in environment - set it to enable OpenAI adapter.")

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        # TODO: implement using openai.ChatCompletion or OpenAI API v1
        raise NotImplementedError("OpenAI adapter not yet implemented in this template.")

    def generate_quiz(self, text: str, num_questions: int = 3):
        raise NotImplementedError("OpenAI adapter not yet implemented in this template.")

    def explain(self, text: str, level: str = "child"):
        raise NotImplementedError("OpenAI adapter not yet implemented in this template.")
