import html
from typing import Dict, List, Optional

import mistune
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name

from .parser import NotebookCell


class CellRenderer:
    """Renders notebook cells to HTML."""

    def __init__(self):
        self.markdown_renderer = mistune.create_markdown()
        self.code_formatter = HtmlFormatter(
            style="default", cssclass="highlight", linenos=False, wrapcode=True
        )

    def render_cell(self, cell: NotebookCell, skip_gradio: bool = False) -> str:
        """Render a single cell to HTML."""
        if cell.cell_type == "markdown":
            return self._render_markdown(cell.source)
        elif cell.cell_type == "code":
            if cell.is_gradio and skip_gradio:
                return ""
            return self._render_code(cell.source)
        else:
            return f"<div class='cell cell-{cell.cell_type}'>{html.escape(cell.source)}</div>"

    def render_gradio_cell(self, gradio_name: str, app_url: str) -> str:
        """Render a Gradio cell with Web Component."""
        return f"""
<div class="cell cell-gradio">
    <gradio-app src="{app_url}" class="gradio-app"></gradio-app>
</div>
"""

    def _render_markdown(self, source: str) -> str:
        """Render markdown source to HTML."""
        return f'<div class="cell cell-markdown">{self.markdown_renderer(source)}</div>'

    def _render_code(self, source: str) -> str:
        """Render code source with syntax highlighting."""
        try:
            lines = source.split("\n")
            first_line = lines[0].strip()

            if first_line.startswith("%%"):
                lang = first_line[2:].split()[0]
                code_source = "\n".join(lines[1:])
            elif first_line.startswith("#"):
                lang = "python"
                code_source = source
            else:
                lang = "python"
                code_source = source

            try:
                lexer = get_lexer_by_name(lang)
            except Exception:
                lexer = TextLexer()

            highlighted = highlight(code_source, lexer, self.code_formatter)
            return f'<div class="cell cell-code"><pre><code>{highlighted}</code></pre></div>'

        except Exception:
            escaped_source = html.escape(source)
            return f'<div class="cell cell-code"><pre><code>{escaped_source}</code></pre></div>'


def render_cells(
    cells: List[NotebookCell], gradio_apps: Optional[Dict[str, str]] = None
) -> str:
    """
    Render a list of cells to HTML.

    Args:
        cells: List of notebook cells
        gradio_apps: Optional dict mapping gradio names to app URLs

    Returns:
        HTML string
    """
    renderer = CellRenderer()
    html_parts = []

    for cell in cells:
        if cell.is_gradio:
            if gradio_apps and cell.gradio_name in gradio_apps:
                html_parts.append(
                    renderer.render_gradio_cell(
                        cell.gradio_name, gradio_apps[cell.gradio_name]
                    )
                )
        else:
            html_parts.append(renderer.render_cell(cell, skip_gradio=False))

    return "\n".join(html_parts)
