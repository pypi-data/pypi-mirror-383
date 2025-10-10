# eduai/__init__.py
from textwrap import dedent

class EduAI:
    def summarize(self, text: str) -> str:
        sentences = text.split(".")
        if len(sentences) > 1:
            return f"Summary: {sentences[0].strip()}."
        return f"Summary: {text[:100]}..."

    def quiz(self, text: str):
        keywords = text.split()[:5]
        return [
            {"question": f"What is '{keywords[0]}'?", "answer": f"It’s a key part of: {text[:50]}..."},
            {"question": f"Why is it mentioned?", "answer": "It’s important in the context of the passage."}
        ]

    def explain(self, concept: str) -> str:
        return f"'{concept}' means something related to its context. Example: '{concept}' helps understanding."

    def simplify(self, text: str) -> str:
        # Just a basic simplification (shorten long words)
        words = text.split()
        simple_words = [w if len(w) < 10 else w[:6] + "..." for w in words]
        return " ".join(simple_words)

    def translate(self, text: str, lang: str) -> str:
        # Mock translation — can later connect to API
        if lang == "ur":
            return f"[Translated to Urdu] {text}"
        elif lang == "es":
            return f"[Traducido al Español] {text}"
        else:
            return f"[Translation not available for '{lang}']"

    def generate_flashcards(self, text: str):
        words = text.split()
        main_word = words[0] if words else "Concept"
        return [
            {"front": f"What is {main_word}?", "back": f"{main_word} is described as part of this text: {text[:60]}..."},
            {"front": f"How is {main_word} used?", "back": "It is used in the main idea of the passage."}
        ]

    def generate_lesson_plan(self, topic: str, grade: int):
        return dedent(f"""
        Lesson Plan: {topic}
        Grade Level: {grade}
        
        Objectives:
        - Understand what the {topic} is.
        - Learn key facts about the {topic}.
        
        Activities:
        - Watch a short video or visual on {topic}.
        - Discuss what students found most interesting.
        - Create a small summary or drawing activity.
        """).strip()
