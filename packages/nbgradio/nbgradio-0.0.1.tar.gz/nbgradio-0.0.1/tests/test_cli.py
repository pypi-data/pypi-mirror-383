"""Tests for the CLI module."""

import tempfile
from pathlib import Path

import click.testing
import nbformat

from nbgradio.cli import cli


def create_test_notebook_file(tmpdir, name="test.ipynb"):
    """Helper to create a test notebook file."""
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_markdown_cell("# Test Notebook"))
    nb.cells.append(nbformat.v4.new_code_cell("print('hello')"))

    notebook_path = Path(tmpdir) / name
    with open(notebook_path, "w") as f:
        nbformat.write(nb, f)

    return notebook_path


def test_cli_no_args():
    """Test CLI with no arguments."""
    runner = click.testing.CliRunner()
    result = runner.invoke(cli)

    assert result.exit_code == 0
    assert "nbgradio" in result.output


def test_cli_build_no_notebooks():
    """Test build command with no notebooks."""
    runner = click.testing.CliRunner()
    result = runner.invoke(cli, ["build"])

    assert result.exit_code == 1
    assert "No notebook files specified" in result.output


def test_cli_build_single_notebook():
    """Test building a single notebook."""
    runner = click.testing.CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test notebook
        notebook_path = create_test_notebook_file(tmpdir)

        # Run build command
        result = runner.invoke(
            cli,
            ["build", str(notebook_path), "--output-dir", str(Path(tmpdir) / "output")],
        )

        # Check success
        assert result.exit_code == 0
        assert "Successfully generated" in result.output

        # Check output files
        output_dir = Path(tmpdir) / "output"
        assert output_dir.exists()
        assert (output_dir / "index.html").exists()
        assert (output_dir / "static" / "style.css").exists()


def test_cli_build_fragment_mode():
    """Test building in fragment mode."""
    runner = click.testing.CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test notebook
        notebook_path = create_test_notebook_file(tmpdir)

        # Run build command with --fragment
        result = runner.invoke(
            cli,
            [
                "build",
                str(notebook_path),
                "--fragment",
                "--output-dir",
                str(Path(tmpdir) / "output"),
            ],
        )

        # Check success
        assert result.exit_code == 0

        # Check fragment output
        fragments_dir = Path(tmpdir) / "output" / "fragments"
        assert fragments_dir.exists()
        assert (fragments_dir / "test.html").exists()


def test_cli_build_multiple_notebooks():
    """Test building multiple notebooks."""
    runner = click.testing.CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple test notebooks
        nb1 = create_test_notebook_file(tmpdir, "notebook1.ipynb")
        nb2 = create_test_notebook_file(tmpdir, "notebook2.ipynb")

        # Run build command
        result = runner.invoke(
            cli,
            ["build", str(nb1), str(nb2), "--output-dir", str(Path(tmpdir) / "output")],
        )

        # Check success
        assert result.exit_code == 0
        assert "Successfully generated" in result.output


def test_cli_build_custom_port():
    """Test building with custom port."""
    runner = click.testing.CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        notebook_path = create_test_notebook_file(tmpdir)

        # Run build command with custom port
        result = runner.invoke(
            cli,
            [
                "build",
                str(notebook_path),
                "--port",
                "8080",
                "--output-dir",
                str(Path(tmpdir) / "output"),
            ],
        )

        # Check that it mentions the custom port
        # Note: The actual server isn't started in tests
        assert result.exit_code == 0


def test_cli_build_nonexistent_notebook():
    """Test building with non-existent notebook."""
    runner = click.testing.CliRunner()

    # Use a temporary directory to ensure the file doesn't exist
    with tempfile.TemporaryDirectory() as tmpdir:
        nonexistent = Path(tmpdir) / "nonexistent.ipynb"

        result = runner.invoke(cli, ["build", str(nonexistent)])

        assert (
            result.exit_code != 0
        )  # Click returns 2 for usage errors, 1 for other errors
        assert "Error" in result.output or "not found" in result.output.lower()


def test_cli_mode_option():
    """Test mode option (local vs spaces)."""
    runner = click.testing.CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        notebook_path = create_test_notebook_file(tmpdir)

        # Test local mode (default)
        result = runner.invoke(
            cli,
            [
                "build",
                str(notebook_path),
                "--mode",
                "local",
                "--output-dir",
                str(Path(tmpdir) / "output"),
            ],
        )

        assert result.exit_code == 0

        # Test spaces mode
        result = runner.invoke(
            cli,
            [
                "build",
                str(notebook_path),
                "--mode",
                "spaces",
                "--output-dir",
                str(Path(tmpdir) / "output_spaces"),
            ],
        )

        # Spaces mode should work but won't actually deploy
        assert result.exit_code == 0
