Here's a README file for your Python project:

---

# Open WebUI Installer

Open WebUI Installer is a desktop application developed by **BrainDrive** for setting up and managing Docker containers that host various flavors of the Open WebUI. The installer automates the process of checking Docker installation, managing container setups, and updating configurations with options tailored for different Open WebUI setups.

## Features

- **Automated Docker Installation**: Detects if Docker is installed, installs it if necessary, and provides setup instructions.
- **Container Management**: Easily start, stop, and update containers, with specific commands for Open WebUI configurations.
- **Flavor Selection**: Choose from multiple Open WebUI flavors, including options for local and remote connections, GPU support, and bundled configurations with Ollama.
- **Logger Integration**: Logs all actions to both the UI and a file, enabling users to monitor setup and troubleshooting steps.

## Getting Started

### Prerequisites

- **Python 3.8+**
- **Docker**
- **Tkinter** for GUI

Ensure you have Python installed and Docker available on your system. The installer will attempt to install Docker if it is not found.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/OpenWebUI_DockerInstaller.git
   cd OpenWebUI_DockerInstaller
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python OpenWebUIInstaller.py
   ```

### Project Structure

- **OpenWebUIInstaller.py**: The main application file that initializes the GUI and manages the setup flow.
- **helpers/docker_manager.py**: Contains the logic for Docker management, including installation, checking container status, and running/updating containers.
- **helpers/option_panel.py**: Manages the flavor selection options displayed in the GUI.
- **helpers/logger.py**: Handles logging to the UI and file for progress tracking.

## Usage

1. **Launch the Application**: Run `main_script.py` to start the Open WebUI Installer.
2. **Install Docker**: Click "Install Docker" if Docker is not already installed on your system.
3. **Set Up Containers**: Choose a flavor from the options panel, then click "Set Up Containers" to initiate the container setup.
4. **Update Containers**: Once containers are set up, you can click "Update Containers" to refresh with the latest configuration.

Each action is logged in the application window and saved in a timestamped file under the `./logs` directory.

### Available Flavors

- **Default (Ollama Local)**: For local installations of Ollama.
- **Ollama Remote**: Connect to Ollama on a remote server.
- **Nvidia GPU Support**: Enables GPU acceleration for supported systems.
- **OpenAI API Only**: Runs Open WebUI with only OpenAI API support.
- **Bundled Ollama with GPU**: GPU-optimized setup bundled with Ollama.
- **Bundled Ollama CPU Only**: CPU-only setup with Ollama.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your improvements.

## Acknowledgments

Open WebUI Installer was developed by **BrainDrive**. Special thanks to the Open WebUI community for supporting the ecosystem.
