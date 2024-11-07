# helpers/docker_manager.py

import subprocess
import platform
import time
import os
import sys

SECONDARY_CONTAINER_COMMAND = [
    "docker", "run", "-d", "-p", "9099:9099", 
    "--add-host=host.docker.internal:host-gateway", 
    "-v", "pipelines:/app/pipelines", 
    "--name", "pipelines", 
    "--restart", "always", 
    "--label", "com.centurylinklabs.watchtower.enable=true",
    "ghcr.io/open-webui/pipelines:main"
]

WATCHTOWER_COMMAND = [
    "docker", "run", "-d",
    "--name", "watchtower",
    "-v", "/var/run/docker.sock:/var/run/docker.sock",
    "containrrr/watchtower",
    "--label-enable"
]

class DockerManager:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self._docker_installed = None
        self._containers_checked_at = 0
        self._containers_running = False

        # Track previous states to log only on status change
        self._previous_docker_installed = None
        self._previous_containers_running = None

    def log(self, message, output_mode="both"):
        """Log a message using the provided callback, with the option to specify output mode."""
        self.log_callback(message, output_mode=output_mode)


    def _run_command(self, command, check=True, shell=False):
        """Run a subprocess command and log real-time output, returning an empty output if it fails."""
        try:
            # Configure the subprocess based on the platform
            if platform.system() == "Windows":
                command_process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=shell,
                    creationflags=subprocess.CREATE_NO_WINDOW  # Suppresses the console window
                )
            else:
                command_process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=shell
                )

            # Capture stdout and stderr
            output, error = command_process.communicate()

            # Log stdout and stderr to the log file
            if output:
                self.log(f"Command output:\n{output.strip()}", output_mode="file")
            if error:
                self.log(f"Command error:\n{error.strip()}", output_mode="file")

            # Check for command success
            if command_process.returncode != 0 and check:
                self.log(f"Command failed with return code {command_process.returncode}.", output_mode="file")
                raise subprocess.CalledProcessError(command_process.returncode, command)
            
            # Return the completed process with output and error
            return subprocess.CompletedProcess(command, command_process.returncode, output, error)
        
        except subprocess.CalledProcessError as e:
            # Log specific command failure details if check=True
            self.log(f"Command failed with error: {e}", output_mode="file")
            return subprocess.CompletedProcess(command, e.returncode, "", e.output or "")
        
        except Exception as e:
            # Log unexpected errors that occur outside of the subprocess call
            self.log(f"Unexpected error running command: {e}", output_mode="file")
            return subprocess.CompletedProcess(command, 1, "", "")
    
    def update_containers(self):
        self.log("Updating Docker containers...", output_mode="both")
        try:
            self.run_container(WATCHTOWER_COMMAND)
            self.log("Containers have update commands executed successfully.", output_mode="both")
        except subprocess.CalledProcessError as e:
            self.log(f"Error updating containers: {e}", output_mode="both")

    def is_docker_installed(self):
        """Check if Docker is installed by running 'docker --version'."""
        try:
            # Run 'docker --version' to verify Docker installation
            result = self._run_command(['docker', '--version'])
            # Set current status based on the return code (0 = success)
            current_status = result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            current_status = False

        # Log only if the status has changed from the last check
        if current_status != self._previous_docker_installed:
            if current_status:
                self.log("Docker is installed.", output_mode="both")
            else:
                self.log("Docker is not installed.", output_mode="both")
            self._previous_docker_installed = current_status

        # Cache the current Docker installation status
        self._docker_installed = current_status
        return current_status



    def is_container_present(self, container_name):
        """
        Check if a specific container exists by name.

        Args:
            container_name (str): The name of the container to check.

        Returns:
            bool: True if the container exists, False otherwise.
        """
        # Ensure Docker is installed before proceeding
        if not self.is_docker_installed():
            self.log(f"Docker is not installed. Cannot check for container '{container_name}'.", output_mode="file")
            return False

        try:
            # Run a command to check if the container exists
            result = self._run_command(
                ['docker', 'ps', '-a', '--filter', f'name={container_name}', '--format', '{{.Names}}']
            )

            # Check if the output contains the container name
            container_exists = container_name in result.stdout.strip()
            if container_exists:
                self.log(f"Container '{container_name}' is present.", output_mode="file")
            else:
                self.log(f"Container '{container_name}' is not present.", output_mode="file")
            return container_exists

        except subprocess.CalledProcessError as e:
            self.log(f"Error checking container '{container_name}': {e}", output_mode="both")
            return False
        

    def are_containers_set_up(self):
        current_time = time.time()
        
        # Limit status check frequency
        if current_time - self._containers_checked_at < 5:
            return self._containers_running

        # Ensure Docker is installed before checking containers
        if not self.is_docker_installed():
            self.log("Docker is not installed. Cannot check container status.", output_mode="both")
            return False

        # Check if any containers are running
        try:
            result = self._run_command(['docker', 'ps', '-q'])
            current_containers_running = bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            current_containers_running = False

        # Log only if container running status has changed
        if current_containers_running != self._previous_containers_running:
            if current_containers_running:
                self.log("Containers are already set up and running.", output_mode="both")
            else:
                self.log("No containers are currently set up.", output_mode="both")
            self._previous_containers_running = current_containers_running

        # Update the cached values
        self._containers_running = current_containers_running
        self._containers_checked_at = current_time
        return current_containers_running

    def install_docker(self):
        os_type = platform.system()
        self.log(f"Starting Docker installation for {os_type}...", output_mode="both")
        try:
            if os_type == "Windows":
                self._install_docker_windows()
            elif os_type == "Darwin":
                self._install_docker_mac()
            elif os_type == "Linux":
                self._install_docker_linux()
            else:
                self.log(f"Unsupported OS: {os_type}", output_mode="both")
                return
            self.log("Docker installed successfully.", output_mode="both")
            self.reset_docker_status()
            time.sleep(5)
        except subprocess.CalledProcessError as e:
            self.log(f"Error installing Docker: {e}", output_mode="both")
            self.reset_docker_status()

    def reset_docker_status(self):
        self._docker_installed = None 

    def _install_docker_windows(self):
        self.log("Installing Docker Desktop for Windows...", output_mode="both")
        self.log(f"Downloading Docker from desktop.docker.com", output_mode="both")
        installer_path = "DockerInstaller.exe"
        docker_url = "https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe"
        self._run_command(["curl", "-L", "-o", installer_path, docker_url])
        self.log(f"Executing DockerInstaller.exe", output_mode="both")
        self._run_command([installer_path, "install"])

    def _install_docker_mac(self):
        self.log("Installing Docker Desktop for macOS...", output_mode="both")
        dmg_path = "Docker.dmg"
        docker_url = "https://desktop.docker.com/mac/stable/Docker.dmg"
        self._run_command(["curl", "-L", "-o", dmg_path, docker_url])
        self._run_command(["hdiutil", "attach", dmg_path])
        self._run_command(["cp", "-r", "/Volumes/Docker/Docker.app", "/Applications"])
        self._run_command(["hdiutil", "detach", "/Volumes/Docker"])

    def _install_docker_linux(self):
        self.log("Installing Docker for Linux...", output_mode="both")
        try:
            self._run_command(["sudo", "apt-get", "update", "-qq"])
            self._run_command(["sudo", "apt-get", "install", "-y", "docker.io"])
            self._run_command(["sudo", "systemctl", "start", "docker"])
            self._run_command(["sudo", "systemctl", "enable", "docker"])
        except subprocess.CalledProcessError:
            self.log("Docker installation failed on Linux.", output_mode="both")

    def run_container(self, command):
        self.log("Running specified Docker container...", output_mode="both")
        self.log("This could take a few minutes to download the image.", output_mode="both")
        try:
            result = self._run_command(command, shell=True)
            if result.returncode == 0:
                self.log("Container started successfully.", output_mode="both")
            else:
                self.log("Failed to start container.", output_mode="both")
                self.log("Please make sure you started docker and signed in.", output_mode="both")
        except subprocess.CalledProcessError as e:
            self.log(f"Error starting container: {e}", output_mode="both")
