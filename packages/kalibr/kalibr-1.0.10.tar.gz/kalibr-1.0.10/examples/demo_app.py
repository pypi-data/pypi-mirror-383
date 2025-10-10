"""
Kalibr Demo App
Demonstrates multi-model schema normalization via Kalibr SDK.
"""

from kalibr.kalibr_app import KalibrApp

app = KalibrApp()

@app.register()
def summarize(text: str) -> str:
    """Summarizes input text."""
    return f"[GPT-style summary]: {text[:40]}..."

@app.register()
def sentiment(text: str) -> dict:
    """Performs sentiment analysis with normalized schema outputs."""
    return {
        "gpt_schema": {"sentiment": "positive", "confidence": 0.91},
        "claude_schema": {"label": "POSITIVE", "probability": 0.89},
        "gemini_schema": {"polarity": 1, "score": 0.92},
    }

@app.register()
def extract_keywords(text: str) -> dict:
    """Extracts key phrases."""
    return {
        "gpt_schema": {"keywords": ["AI", "automation", "infrastructure"]},
        "claude_schema": {"phrases": ["AI", "automation", "infra"]},
        "gemini_schema": {"entities": ["AI", "automation", "infra"]},
    }
