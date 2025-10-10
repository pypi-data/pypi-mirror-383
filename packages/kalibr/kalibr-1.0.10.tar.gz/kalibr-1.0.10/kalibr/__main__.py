import typer
import os
import sys
import subprocess

app = typer.Typer(help="Kalibr Connect CLI")

def banner():
    print("\n🚀 Kalibr SDK (Demo Mode)")
    print("⚠️  Running in local evaluation mode.")
    print("💡  To enable production or hosted runtime, visit https://kalibr.systems\n")

@app.command(help="Run a Kalibr app locally.")
def serve(file: str):
    """
    Run a Kalibr app locally.
    Example: kalibr-connect serve demo_app.py
    """
    banner()
    print(f"🚀 Serving {file} locally...")
    subprocess.run(["uvicorn", f"{file.replace('.py', '')}:app", "--reload"])

@app.command(help="Deploy a Kalibr app (stubbed demo).")
def deploy(file: str):
    """
    Stubbed deploy command for demo/testing.
    """
    banner()
    print(f"⚙️  Deployment is only available for licensed users.")
    print(f"   Visit https://kalibr.systems for API access.\n")

@app.command(help="Show this usage guide.")
def usage():
    print("""
Kalibr Connect Commands:
  kalibr-connect serve <file>   Run a Kalibr app locally.
  kalibr-connect deploy <file>  Deploy your Kalibr app (stubbed demo).
  kalibr-connect usage          Show this usage guide.
    """)

def main():
    api_key = os.getenv("KALIBR_API_KEY")
    if not api_key:
        print("⚠️  No API key detected. Running in local demo mode.")
    app()

if __name__ == "__main__":
    main()
