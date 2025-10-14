# nbgradio 🧩

Convert Jupyter notebooks to static HTML websites with **live Gradio apps** embedded using Web Components.

## 🚀 Features

- **📖 Notebook Parsing**: Convert `.ipynb` files to static HTML
- **⚡ Live Gradio Apps**: Embed interactive Gradio apps directly in your static site
- **🎨 Syntax Highlighting**: Beautiful code highlighting using Pygments
- **📱 Responsive Design**: Mobile-friendly layouts with modern CSS
- **🔧 Flexible Output**: Generate full HTML pages or embeddable fragments
- **🖥️ Local Development**: Built-in local server for testing Gradio apps

## 📦 Installation

```bash
pip install nbgradio
```

## 🛠️ Usage

### Quickstart

Try nbgradio instantly with our example notebook:

```bash
nbgradio build https://github.com/gradio-app/nbgradio/blob/main/test_notebook.ipynb
```

This will:
- Download the example notebook from GitHub
- Parse the Gradio app (`#nbgradio name="greet"`)
- Generate a static HTML site with the live app embedded
- Start a local server at `http://localhost:7860`

Open your browser to see the result! The notebook contains a simple greeting app that you can interact with.

### Basic Usage

Create a Jupyter notebook with Gradio cells marked with the `#nbgradio` comment:

```python
#nbgradio name="greet"
import gradio as gr

def greet(name):
    return f"Hello {name}!"

demo = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(label="Your name"),
    outputs=gr.Textbox(label="Greeting")
)

demo.launch()
```

Then build your static site:

```bash
nbgradio build notebook.ipynb
```

This generates a `site/` directory with:
- `index.html` - Your notebook as a static HTML page with live Gradio apps
- `static/style.css` - Styling for the page
- Local Gradio server running at `http://localhost:7860`

### Advanced Usage

#### Multiple Notebooks
```bash
nbgradio build notebook1.ipynb notebook2.ipynb --output-dir my-site
```

#### Fragment Mode (for embedding)
```bash
nbgradio build notebook.ipynb --fragment --output-dir fragments
```

#### Custom Port
```bash
nbgradio build notebook.ipynb --port 8080
```

#### Using URLs
```bash
# GitHub notebooks (automatically converts blob URLs to raw)
nbgradio build https://github.com/user/repo/blob/main/notebook.ipynb

# Direct notebook URLs
nbgradio build https://example.com/notebook.ipynb

# Mix local files and URLs
nbgradio build local.ipynb https://github.com/user/repo/blob/main/remote.ipynb
```

### Deploying to Hugging Face Spaces

Deploy your Gradio apps directly to Hugging Face Spaces for public hosting:

```bash
nbgradio build notebook.ipynb --spaces
```

This will:
- Prompt you to login to Hugging Face if not already authenticated
- Create Spaces named `{username}/{app_name}` for each Gradio app
- Deploy each app with proper README and `nbgradio` tag
- Return URLs pointing to your live Spaces

#### Why Deploy to Spaces?

**Perfect for Static Hosting**: This is especially useful if you're deploying your static site to platforms like GitHub Pages, Netlify, or Vercel. These platforms can serve your static HTML, but they can't run Python/Gradio apps. By deploying the interactive components to Spaces, you get:

- **Static HTML** → Hosted on GitHub Pages/Netlify (fast, free, CDN)
- **Interactive Apps** → Hosted on Spaces (Python runtime, Gradio support)
- **Seamless Integration** → Web Components automatically connect the two

#### Overwriting Existing Spaces

If a Space already exists, nbgradio will check if it was created with nbgradio (has the `nbgradio` tag):

```bash
# Safe update of existing nbgradio spaces
nbgradio build notebook.ipynb --spaces

# Overwrite any existing space (use with caution)
nbgradio build notebook.ipynb --spaces --overwrite
```

### Gradio Cell Syntax

Mark cells with `#nbgradio name="app_name"`:

```python
#nbgradio name="calculator"
import gradio as gr

def calculate(operation, a, b):
    if operation == "add":
        return a + b
    elif operation == "multiply":
        return a * b
    return 0

demo = gr.Interface(
    fn=calculate,
    inputs=[
        gr.Radio(["add", "multiply"], label="Operation"),
        gr.Number(label="First number"),
        gr.Number(label="Second number")
    ],
    outputs=gr.Number(label="Result")
)

demo.launch()
```

**Key Points:**
- Multiple cells with the same `name` are concatenated
- The `demo.launch()` call is automatically removed
- Apps are mounted at `http://localhost:7860/{app_name}`

## 📁 Output Structure

```
site/
├── index.html              # Main HTML page
├── fragments/              # HTML fragments (with --fragment)
│   └── notebook_name.html
└── static/
    └── style.css           # CSS with syntax highlighting
```

## 🎨 HTML Output

Generated HTML includes:

- **Markdown cells** → Rendered HTML with styling
- **Code cells** → Syntax-highlighted code blocks
- **Gradio cells** → Live `<gradio-app>` Web Components

```html
<gradio-app src="http://localhost:7860/greet" class="gradio-app"></gradio-app>
```

## ⚙️ CLI Reference

```bash
nbgradio build [OPTIONS] NOTEBOOKS...
```

**NOTEBOOKS:** One or more Jupyter notebook files (.ipynb) or URLs

**Options:**
- `--mode [local|spaces]` - Deployment mode (default: local)
- `--spaces` - Deploy Gradio apps to Hugging Face Spaces
- `--overwrite` - Overwrite existing Spaces (use with caution)
- `--fragment` - Output HTML fragments instead of full pages
- `--output-dir PATH` - Output directory (default: site)
- `--port INTEGER` - Port for local Gradio apps (default: 7860)
- `--theme TEXT` - Theme for generated site (not yet implemented)

## 🧪 Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/
```

### Code Quality

```bash
ruff check nbgradio/ tests/
ruff format nbgradio/ tests/
```

## 📄 Requirements

- Python ≥ 3.9
- Jupyter notebooks with nbformat ≥ 5.0
- Gradio ≥ 4.0

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/gradio-app/nbgradio)
- [PyPI Package](https://pypi.org/project/nbgradio/)
- [Gradio Documentation](https://gradio.app/docs/)