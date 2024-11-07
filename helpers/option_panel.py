# helpers/option_panel.py

import tkinter as tk
from tkinter import ttk

class OptionPanel(ttk.LabelFrame):
    def __init__(self, parent, log_callback):
        super().__init__(parent, text="Options")
        self.log_callback = log_callback

        # Dropdown for flavor selection
        self.flavor_var = tk.StringVar()
        self.flavor_options = {
            "Default (Ollama Local)": "docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always --label com.centurylinklabs.watchtower.enable=true ghcr.io/open-webui/open-webui:main",
            "Ollama Remote": "docker run -d -p 3000:8080 -e OLLAMA_BASE_URL=https://example.com -v open-webui:/app/backend/data --name open-webui --restart always --label com.centurylinklabs.watchtower.enable=true ghcr.io/open-webui/open-webui:main",
            "Nvidia GPU Support": "docker run -d -p 3000:8080 --gpus all --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always --label com.centurylinklabs.watchtower.enable=true ghcr.io/open-webui/open-webui:cuda",
            "OpenAI API Only": "docker run -d -p 3000:8080 -e OPENAI_API_KEY=your_secret_key -v open-webui:/app/backend/data --name open-webui --restart always --label com.centurylinklabs.watchtower.enable=true ghcr.io/open-webui/open-webui:main",
            "Bundled Ollama with GPU": "docker run -d -p 3000:8080 --gpus=all -v ollama:/root/.ollama -v open-webui:/app/backend/data --name open-webui --restart always --label com.centurylinklabs.watchtower.enable=true ghcr.io/open-webui/open-webui:ollama",
            "Bundled Ollama CPU Only": "docker run -d -p 3000:8080 -v ollama:/root/.ollama -v open-webui:/app/backend/data --name open-webui --restart always --label com.centurylinklabs.watchtower.enable=true ghcr.io/open-webui/open-webui:ollama"
        }

        # Descriptions for each option
        self.flavor_descriptions = {
            "Default (Ollama Local)": "Use this option if Ollama is installed locally on your machine.",
            "Ollama Remote": "Connect to Ollama on a different server by setting OLLAMA_BASE_URL.",
            "Nvidia GPU Support": "Enable GPU support for accelerated performance on Nvidia hardware.",
            "OpenAI API Only": "Run Open WebUI with only OpenAI API support, providing your API key.",
            "Bundled Ollama with GPU": "Install a bundled setup with Ollama, optimized for GPU usage.",
            "Bundled Ollama CPU Only": "Install a bundled setup with Ollama, running on CPU only."
        }

        self.flavor_menu = ttk.Combobox(self, textvariable=self.flavor_var, values=list(self.flavor_options.keys()), state="readonly", width=35)
        self.flavor_menu.set("Select Flavor")
        self.flavor_menu.pack(padx=10, pady=5)

        # Bind the dropdown to display a description when an option is selected
        self.flavor_menu.bind("<<ComboboxSelected>>", self.display_description)


    def display_description(self, event):
        """Display description of the selected option."""
        selected_flavor = self.flavor_var.get()
        description = self.flavor_descriptions.get(selected_flavor, "")
        # self.description_label.config(text=description)
        
        # Optionally log the description as well
        self.log_callback(description)

    def get_selected_flavor_command(self):
        """Return the Docker command based on the selected flavor."""
        flavor = self.flavor_var.get()
        return self.flavor_options.get(flavor, "")
