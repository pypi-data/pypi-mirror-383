# Kalibr SDK

**Multi-Model AI Integration Framework**

Write once. Deploy anywhere. Connect to any AI model.

Kalibr lets developers expose any Python function as a model-compatible API — instantly usable by GPT, Claude, Gemini, and beyond.

---

## 🚀 Quick Start

### Install
```bash
pip install kalibr
```

### Run the included demo
```bash
kalibr-connect serve examples/demo_app.py
```

Then open your browser to:
```
http://127.0.0.1:8000/docs
```
You’ll see automatically generated endpoints for your demo functions — all schema-normalized and model-ready.

---

## ⚙️ Core Features

✅ **Multi-Model Support** — Works with GPT Actions, Claude MCP, Gemini, and Copilot  
✅ **Automatic Schema Generation** — Define once, serve everywhere  
✅ **Fast Local Development** — Instantly test endpoints with `kalibr-connect serve`  
✅ **Lightweight Runtime** — No dependencies beyond FastAPI + Uvicorn  

🚧 *Coming Soon:*  
• Auth & JWT user sessions  
• Analytics & observability  
• One-click deployment (Fly.io, AWS Lambda)

---

## 🧠 How It Works

Decorate your Python functions with `@app.register()`:

```python
from kalibr.kalibr_app import KalibrApp

app = KalibrApp()

@app.register()
def summarize(text: str) -> str:
    """Summarize text input."""
    return text[:100] + "..."

@app.register()
def sentiment(text: str) -> dict:
    """Return a basic sentiment classification."""
    return {"sentiment": "positive" if "love" in text.lower() else "neutral"}

kalibr_app = app.get_app()
```

Then run:
```bash
kalibr-connect serve demo_app.py
```

Your endpoints appear instantly at:
```
http://127.0.0.1:8000/docs
```

---

## 📁 Project Structure

```
kalibr/
  ├── __init__.py
  ├── __main__.py
  ├── kalibr_app.py
  ├── schema_generators.py
examples/
  ├── demo_app.py
  └── enhanced_kalibr_example.py
```

---

## 📘 Documentation

See [KALIBR_SDK_COMPLETE.md](KALIBR_SDK_COMPLETE.md) for full developer documentation.

---

**Kalibr — Transform how you build AI-integrated applications.**
