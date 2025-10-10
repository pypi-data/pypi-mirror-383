import typer
from kalibr.kalibr_app import serve_app, deploy_app

cli = typer.Typer(help="Kalibr Connect CLI")

@cli.command("serve")
def serve(file: str):
    """Run a Kalibr app locally."""
    serve_app(file)

@cli.command("deploy")
def deploy(file: str):
    """Deploy a Kalibr app."""
    deploy_app(file)

@cli.command("usage")
def usage():
    """Show usage guide."""
    print("""
Kalibr Connect Commands:
  kalibr-connect serve <file>   Run a Kalibr app locally.
  kalibr-connect deploy <file>  Deploy your Kalibr app.
  kalibr-connect usage          Show this usage guide.
""")

def main():
    """Entry point for console_scripts."""
    cli()

if __name__ == "__main__":
    main()
