from fastapi import FastAPI
import importlib.util
import json
import inspect
from pydantic import BaseModel

class KalibrApp:
    """
    Minimal Kalibr SDK App that auto-generates schemas
    for GPT Actions, Claude MCP, Gemini, etc.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.app = FastAPI(title="Kalibr App")
        self.functions = self._load_tools()

    def _load_tools(self):
        """Dynamically import all @tool-decorated functions from the user app."""
        spec = importlib.util.spec_from_file_location("user_app", self.file_path)
        user_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_app)
        funcs = {}

        for name, obj in inspect.getmembers(user_app, inspect.isfunction):
            if hasattr(obj, "_kalibr_tool"):
                funcs[name] = obj
                self._register_route(name, obj)

        return funcs

    def _register_route(self, name, func):
        """Register each tool as a POST endpoint."""
        class RequestSchema(BaseModel):
            __annotations__ = {k: v for k, v in func.__annotations__.items() if k != "return"}

        async def route(payload: RequestSchema):
            result = func(**payload.dict())
            return {"result": result}

        self.app.post(f"/tools/{name}")(route)

    def generate_schemas(self):
        """Generate model-specific schemas for GPT Actions, Claude MCP, Gemini."""
        schemas = {}
        for name, func in self.functions.items():
            sig = inspect.signature(func)
            params = {
                k: str(v.annotation) for k, v in sig.parameters.items()
            }
            schemas[name] = {
                "description": func.__doc__ or "",
                "parameters": params,
                "returns": str(sig.return_annotation),
            }
        return {
            "gpt_actions": schemas,
            "claude_mcp": schemas,
            "gemini_tools": schemas,
        }

def serve_app(file_path: str):
    """Run the Kalibr app locally."""
    from uvicorn import run
    app_instance = KalibrApp(file_path)
    print("✅ Generated Schemas:")
    print(json.dumps(app_instance.generate_schemas(), indent=2))
    run(app_instance.app, host="127.0.0.1", port=8000)
