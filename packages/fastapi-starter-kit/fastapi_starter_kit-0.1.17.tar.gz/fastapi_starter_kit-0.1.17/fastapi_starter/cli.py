import click
from pathlib import Path
import shutil
from importlib import resources

def copy_template_to(dest: str):
    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)

    template_pkg = resources.files("fastapi_starter").joinpath("template")
    with resources.as_file(template_pkg) as tmpl_root:
        shutil.copytree(tmpl_root, dest_path, dirs_exist_ok=True)


@click.command()
@click.argument("project_name")
def startproject(project_name):
    """Create a new FastAPI project."""
    click.secho(f"🚀 Creating new FastAPI Starter project: {project_name}", fg="cyan")
    copy_template_to(project_name)
    click.secho(f"✅ Project '{project_name}' created successfully!", fg="green")

    # Project Features
    click.secho("\n🛠  Features included in this project:", fg="cyan", bold=True)
    features = [
        "JWT authentication (login/logout, token refresh)",
        "User registration endpoint with hashed password",
        "Modular project structure with routers, services, and models",
        "Database setup with SQLAlchemy and Alembic migrations",
        "Environment configuration using python-dotenv",
        "Pre-configured middleware, exception handling, and logging",
        "Ready-to-use FastAPI project to start development immediately"
    ]
    for feat in features:
        click.secho(f"  ▶ {feat}", fg="yellow")

    # Next steps
    click.secho("\n📌 Next steps:", fg="cyan", bold=True)
    click.secho(f"  1. Navigate to your project folder:", fg="cyan", bold=True)
    click.secho(f"       cd {project_name}", fg="yellow")
    click.secho(f"  2. Start your FastAPI app:", fg="cyan", bold=True)
    click.secho(f"       python main.py", fg="yellow")
    click.secho(f"       # or for auto-reload during development:", fg="yellow")
    click.secho(f"       uvicorn main:app --reload", fg="yellow")
    click.secho(f"  3. Initialize the database and create default tables:", fg="cyan", bold=True)
    click.secho(f"       alembic upgrade head", fg="yellow")

    click.secho("\n🎉 You're ready to start developing your FastAPI project!\n", fg="magenta", bold=True)

def main():
    """Entry point for the CLI."""
    # Click handles the command-line arguments parsing automatically
    startproject.main(standalone_mode=True)

if __name__ == "__main__":
    main()
