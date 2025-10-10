import importlib.util
import os
import uvicorn
from fastapi import FastAPI

class KalibrApp(FastAPI):
    def __init__(self):
        super().__init__()
        print("🚀 KalibrApp initialized. Ready to serve AI tools.")

    def run(self, host="127.0.0.1", port=8000):
        print(f"🚀 Starting Kalibr server on http://{host}:{port}")
        uvicorn.run(self, host=host, port=port)

# --- CLI helper functions ---

def serve_app(file_path: str):
    """Run a Kalibr app file (e.g. demo_app.py) locally."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    app = getattr(module, "app", None)
    if not app:
        print("❌ No `app` instance found in the provided file.")
        return

    print(f"🚀 Serving {file_path} locally...")
    uvicorn.run(app, host="127.0.0.1", port=8000)

def deploy_app(file_path: str):
    """Stub for future deploy command."""
    print(f"🚀 Deploying {file_path} (stub). Future versions will handle cloud deploys.")
