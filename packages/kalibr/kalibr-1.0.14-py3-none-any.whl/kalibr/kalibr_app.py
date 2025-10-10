import os
import sys
import typer
import uvicorn
import importlib.util
from fastapi import FastAPI
from rich.console import Console

console = Console()


class KalibrApp(FastAPI):
    """Lightweight FastAPI wrapper with a .tool() decorator."""
    def tool(self):
        def decorator(func):
            self.get(f"/{func.__name__}")(func)
            return func
        return decorator


app = typer.Typer(help="Kalibr Connect CLI")


def load_app_from_file(file_path: str):
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {abs_path}")

    spec = importlib.util.spec_from_file_location("user_app", abs_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["user_app"] = module
    spec.loader.exec_module(module)

    if not hasattr(module, "app"):
        raise AttributeError("No FastAPI app instance named 'app' found in the file.")
    return module.app


@app.command("serve")
def serve(file: str):
    """Run a Kalibr app locally from a .py file."""
    console.print(f"[cyan]🚀 Serving {file} locally...[/cyan]")
    try:
        app_instance = load_app_from_file(file)
        console.print("[green]✅ App loaded successfully. Starting server...[/green]")
        uvicorn.run(app_instance, host="127.0.0.1", port=8000, reload=False)
    except Exception as e:
        console.print(f"[red]❌ Failed to start app:[/red] {e}")


@app.command("deploy")
def deploy(file: str):
    console.print(f"[yellow]🚀 Deploying {file} (stub)...[/yellow]")


@app.command("usage")
def usage():
    console.print(
        "\n[bold cyan]Kalibr Connect Commands:[/bold cyan]\n"
        "  kalibr-connect serve <file>   Run a Kalibr app locally.\n"
        "  kalibr-connect deploy <file>  Deploy your Kalibr app.\n"
        "  kalibr-connect usage          Show this usage guide.\n"
    )


def run():
    app()


if __name__ == "__main__":
    run()
