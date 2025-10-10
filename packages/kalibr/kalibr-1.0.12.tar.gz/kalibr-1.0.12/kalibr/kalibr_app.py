from fastapi import FastAPI
from typing import Callable

class KalibrApp:
    def __init__(self):
        self.app = FastAPI(title="Kalibr SDK App")
        self._routes = []

    def register(self):
        """
        Decorator to register a Python function as a Kalibr tool endpoint.
        Exposes the function automatically with JSON schema inference.
        """
        def decorator(func: Callable):
            route_path = f"/{func.__name__}"
            self.app.post(route_path)(func)
            self._routes.append(func.__name__)
            return func
        return decorator

    def get_app(self):
        """Return the FastAPI instance."""
        return self.app


# Default export for uvicorn (if someone runs `kalibr-connect serve demo_app.py`)
app = KalibrApp().get_app()
