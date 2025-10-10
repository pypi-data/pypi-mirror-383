"""
Fallback model adapter that requires no external API keys.
Simple heuristics to be useful offline and immediately.
"""

import re
from typing import List, Dict

def _split_sentences(text):
    # very naive sentence splitter
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

class FallbackModel:
    def summarize(self, text: str, max_sentences: int = 3) -> str:
        sents = _split_sentences(text)
        if not sents:
            return ""
        # choose first, middle, last as a crude summary if available
        picks = []
        if len(sents) <= max_sentences:
            picks = sents
        else:
            picks = [sents[0]]
            mid = sents[len(sents)//2]
            if mid not in picks:
                picks.append(mid)
            if sents[-1] not in picks and len(picks) < max_sentences:
                picks.append(sents[-1])
            picks = picks[:max_sentences]
        return " ".join(picks)

    def generate_quiz(self, text: str, num_questions: int = 3) -> List[Dict]:
        sents = _split_sentences(text)
        if not sents:
            return []
        questions = []
        # use first <num_questions> sentences to create simple fill-in-the-blank questions
        for i, sent in enumerate(sents[:num_questions]):
            words = [w for w in re.findall(r"\w+", sent) if len(w) > 3]
            answer = words[-1] if words else ""
            prompt = sent.replace(answer, "_____", 1) if answer else sent + " (short answer)"
            # simple wrong choices by altering last letter
            choices = []
            if answer:
                choices = [answer, answer + "a", answer[:-1] + "x" if len(answer) > 1 else answer + "x", answer[::-1]]
                # ensure uniqueness and length 4
                seen = set()
                uniq = []
                for c in choices:
                    if c not in seen:
                        uniq.append(c)
                        seen.add(c)
                    if len(uniq) >= 4:
                        break
                choices = uniq
            questions.append({
                "id": i+1,
                "question": prompt,
                "answer": answer,
                "choices": choices
            })
        return questions

    def explain(self, text: str, level: str = "child") -> str:
        # very simple "explain like I'm X" implementation
        base = self.summarize(text, max_sentences=2)
        if level.lower() in ("child", "kid", "5", "6"):
            return f"Here is a simple explanation: {base}. In short: {base}"
        else:
            return f"Explanation: {base}. More details can be added with a real model."
