# eduai

A small educational Python package for **children and teachers**.
This repository contains a usable fallback model so the package works immediately
without API keys, plus templates you can extend to add OpenAI/Gemini adapters.

## What's included

- `eduai/` package with core engine and a `FallbackModel` (works offline).
- Templates for `openai_model.py` and `gemini_model.py` (not implemented).
- CLI: `python -m eduai.cli demo --mode summarize|quiz|explain`
- Example script: `python examples/demo_run.py`
- `pyproject.toml`, `requirements.txt`, `LICENSE` (MIT)

## Quickstart

1. (Optional) Create a virtualenv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies (optional; fallback works without them):
   ```bash
   pip install -r requirements.txt
   ```
3. Run the demo:
   ```bash
   python -m eduai.cli demo --mode summarize
   python -m eduai.cli demo --mode quiz
   python -m eduai.cli demo --mode explain
   ```

## Extending with real models

- Implement `eduai.models.openai_model.OpenAIModel` and call it with `EduAI(model_name='openai', model_adapter=OpenAIModel(...))`.
- Implement Gemini adapter in `eduai/models/gemini_model.py`.

