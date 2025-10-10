from kalibr.kalibr_app import KalibrApp

# Initialize the Kalibr app
app = KalibrApp(title="Demo App")

# Example tool
@app.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@app.tool()
def greet(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}! This response is generated via Kalibr."

# Expose the FastAPI instance for uvicorn
asgi_app = app.fastapi_app
