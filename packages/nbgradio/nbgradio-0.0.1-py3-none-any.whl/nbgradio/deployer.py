import threading
import io
import os
from pathlib import Path
from typing import Dict, List

import gradio as gr
import uvicorn
import huggingface_hub
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from huggingface_hub.errors import RepositoryNotFoundError
from requests import HTTPError


class GradioAppManager:
    """Manages Gradio app execution and deployment."""

    def __init__(self, mode: str = "local", port: int = 7860, output_dir: Path = None, overwrite: bool = False):
        self.mode = mode
        self.port = port
        self.output_dir = output_dir or Path("site")
        self.overwrite = overwrite
        self.apps = {}
        self.fastapi_app = None
        self.server_thread = None
        self.server = None

    def execute_gradio_cells(
        self, gradio_cells: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """Execute Gradio cells and return app URLs."""
        if not gradio_cells:
            return {}

        app_urls = {}

        for app_name, code_strings in gradio_cells.items():
            try:
                full_code = "\n".join(code_strings)

                lines = full_code.split("\n")
                lines = [
                    line for line in lines if not line.strip().startswith("#nbgradio")
                ]

                modified_lines = []
                for line in lines:
                    if ".launch()" in line:
                        continue
                    modified_lines.append(line)
                full_code = "\n".join(modified_lines)

                namespace = {
                    "__builtins__": __builtins__,
                    "gr": gr,
                    "gradio": gr,
                }

                exec(full_code, namespace)

                gradio_app = None
                for key, value in namespace.items():
                    if isinstance(value, (gr.Interface, gr.Blocks, gr.ChatInterface)):
                        gradio_app = value
                        break

                if gradio_app is None:
                    print(f"Warning: No Gradio app found in {app_name}")
                    continue

                if hasattr(gradio_app, 'dev_mode'):
                    gradio_app.dev_mode = False

                if self.mode == "local":
                    self.apps[app_name] = gradio_app
                    app_urls[app_name] = f"http://localhost:{self.port}/{app_name}"
                elif self.mode == "spaces":
                    space_url = self._deploy_to_space(app_name, full_code)
                    app_urls[app_name] = space_url
                else:
                    app_urls[app_name] = f"https://huggingface.co/spaces/{app_name}"

            except Exception as e:
                print(f"Error executing Gradio app '{app_name}': {e}")
                import traceback
                traceback.print_exc()
                continue

        return app_urls

    def start_local_server(self):
        """Start the local FastAPI server with mounted Gradio apps and main page."""
        self.fastapi_app = FastAPI(title="nbgradio Development Server")

        self.fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        static_dir = self.output_dir / "static"
        if static_dir.exists():
            self.fastapi_app.mount(
                "/static", StaticFiles(directory=str(static_dir)), name="static"
            )

        for app_name, gradio_app in self.apps.items():
            gr.mount_gradio_app(
                self.fastapi_app, 
                gradio_app, 
                path=f"/{app_name}"
            )

        index_file = self.output_dir / "index.html"
        if index_file.exists():

            @self.fastapi_app.get("/")
            async def serve_main_page():
                return FileResponse(str(index_file))

        config = uvicorn.Config(
            self.fastapi_app, 
            host="0.0.0.0", 
            port=self.port, 
            log_level="warning"
        )
        self.server = uvicorn.Server(config)

        self.server_thread = threading.Thread(target=self.server.run, daemon=True)
        self.server_thread.start()

        print(f"✅ nbgradio development server started!")
        print(f"   📖 Main page: http://localhost:{self.port}/")
        for app_name in self.apps:
            print(f"   ⚡ Gradio app '{app_name}': http://localhost:{self.port}/{app_name}")

    def stop_local_server(self):
        """Stop the local server."""
        if self.server:
            self.server.should_exit = True

    def _deploy_to_space(self, app_name: str, code: str) -> str:
        """Deploy a Gradio app to Hugging Face Spaces."""
        hf_api = huggingface_hub.HfApi()
        
        # Check if user is logged in
        token = huggingface_hub.utils.get_token()
        if not token:
            print("Please login to Hugging Face:")
            huggingface_hub.login(add_to_git_credential=False)
            token = huggingface_hub.utils.get_token()
        
        # Get username
        user_info = hf_api.whoami(token=token)
        username = user_info["name"]
        space_id = f"{username}/{app_name}"
        
        # Check if space exists
        try:
            repo_info = hf_api.repo_info(space_id, repo_type="space")
            # Check if it has nbgradio tag
            if "nbgradio" not in repo_info.tags:
                if not self.overwrite:
                    raise ValueError(f"Space {space_id} already exists and was not created with nbgradio. Either delete this space or pass in --overwrite flag if you are SURE that you'd like to overwrite this space.")
                print(f"Overwriting existing space: {space_id}")
            else:
                print(f"Updating existing nbgradio space: {space_id}")
        except RepositoryNotFoundError:
            print(f"Creating new space: {space_id}")
        
        # Create or update the space
        try:
            huggingface_hub.create_repo(
                space_id,
                private=False,
                space_sdk="gradio",
                repo_type="space",
                exist_ok=True,
            )
        except HTTPError as e:
            if e.response.status_code in [401, 403]:
                print("Need 'write' access token to create a Spaces repo.")
                huggingface_hub.login(add_to_git_credential=False)
                huggingface_hub.create_repo(
                    space_id,
                    private=False,
                    space_sdk="gradio",
                    repo_type="space",
                    exist_ok=True,
                )
            else:
                raise ValueError(f"Failed to create Space: {e}")
        
        # Create README.md
        readme_content = f"""---
title: {app_name}
emoji: 🤗
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: {gr.__version__}
app_file: app.py
pinned: false
tags:
- nbgradio
---

# {app_name}

This Gradio app was created with nbgradio.
"""
        
        readme_buffer = io.BytesIO(readme_content.encode("utf-8"))
        hf_api.upload_file(
            path_or_fileobj=readme_buffer,
            path_in_repo="README.md",
            repo_id=space_id,
            repo_type="space",
        )
        
        # Create app.py
        app_buffer = io.BytesIO(code.encode("utf-8"))
        hf_api.upload_file(
            path_or_fileobj=app_buffer,
            path_in_repo="app.py",
            repo_id=space_id,
            repo_type="space",
        )
        
        # Add nbgradio tag
        hf_api.add_space_tag(space_id, "nbgradio")
        
        space_url = f"https://huggingface.co/spaces/{space_id}"
        print(f"✅ Deployed {app_name} to {space_url}")
        return space_url


_manager = None


def deploy_gradio_apps(
    gradio_cells: Dict[str, List[str]], 
    mode: str = "local", 
    port: int = 7860, 
    output_dir: Path = None,
    overwrite: bool = False
) -> Dict[str, str]:
    """Deploy Gradio apps and return their URLs."""
    global _manager

    if _manager and _manager.server:
        _manager.stop_local_server()
    _manager = GradioAppManager(mode=mode, port=port, output_dir=output_dir, overwrite=overwrite)

    app_urls = _manager.execute_gradio_cells(gradio_cells)

    if mode == "local":
        _manager.start_local_server()

    return app_urls