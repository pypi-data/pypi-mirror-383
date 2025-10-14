import sys
from pathlib import Path
from typing import List

import click

from .builder import build_notebooks
from .parser import parse_notebooks


@click.group()
def cli():
    """nbgradio - Convert Jupyter notebooks to static HTML websites with live Gradio apps."""
    pass


@cli.command()
@click.argument("notebooks", nargs=-1, type=str)
@click.option(
    "--mode",
    type=click.Choice(["local", "spaces"]),
    default="local",
    help="Deployment mode for Gradio apps",
)
@click.option("--spaces", is_flag=True, help="Deploy Gradio apps to Hugging Face Spaces")
@click.option("--overwrite", is_flag=True, help="Overwrite existing Spaces (use with caution)")
@click.option(
    "--fragment", is_flag=True, help="Output HTML fragments instead of full pages"
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default="site",
    help="Output directory for generated files",
)
@click.option("--port", type=int, default=7860, help="Port for local Gradio apps")
@click.option("--theme", help="Theme for the generated site (not implemented)")
def build(
    notebooks: List[str],
    mode: str,
    spaces: bool,
    overwrite: bool,
    fragment: bool,
    output_dir: Path,
    port: int,
    theme: str,
):
    """
    Build static HTML websites from Jupyter notebooks with live Gradio apps.

    NOTEBOOKS: One or more Jupyter notebook files (.ipynb) or URLs
    """
    if not notebooks:
        click.echo("Error: No notebook files specified", err=True)
        sys.exit(1)

    # Validate notebooks (check if local files exist)
    for notebook in notebooks:
        if not notebook.startswith(('http://', 'https://')):
            notebook_path = Path(notebook)
            if not notebook_path.exists():
                click.echo(f"Error: Notebook file not found: {notebook}", err=True)
                sys.exit(1)

    try:
        click.echo(f"Parsing {len(notebooks)} notebook(s)...")
        notebook_data = parse_notebooks(notebooks)

        if spaces:
            click.echo("Deploying to Hugging Face Spaces...")
            generated_files = build_notebooks(
                notebook_data=notebook_data,
                output_dir=output_dir,
                fragment_only=fragment,
                mode="spaces",
                port=port,
                overwrite=overwrite,
            )
        else:
            click.echo(f"Building HTML output in {output_dir}...")
            generated_files = build_notebooks(
                notebook_data=notebook_data,
                output_dir=output_dir,
                fragment_only=fragment,
                mode=mode,
                port=port,
            )

        click.echo(f"Successfully generated {len(generated_files)} file(s):")
        for file_path in generated_files:
            click.echo(f"  - {file_path}")

        if mode == "local":
            click.echo("\n🚀 Development server ready!")
            click.echo(f"   📖 View your notebook: http://localhost:{port}/")
            click.echo(f"   ⚡ Individual Gradio apps available at: http://localhost:{port}/<app_name>")
            click.echo("\n💡 Tip: The main page shows your full notebook with embedded Gradio apps")
            click.echo("   Press Ctrl+C to stop the server")
            
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                click.echo("\n👋 Server stopped. Goodbye!")
                return

    except KeyboardInterrupt:
        click.echo("\n👋 Server stopped. Goodbye!")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point for the nbgradio CLI."""
    cli()


if __name__ == "__main__":
    main()
