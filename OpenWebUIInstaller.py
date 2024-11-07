# main_script.py

import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
from datetime import datetime
from helpers.docker_manager import DockerManager, SECONDARY_CONTAINER_COMMAND
from helpers.option_panel import OptionPanel
from helpers.logger import Logger

class OpenWebUIInstaller(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Open WebUI Installer By BrainDrive (v0.1)")
        self.geometry("700x450")
        # self.bind("<FocusIn>", lambda event: self.after(100, self.update_button_states))

        # Create the logs directory if it doesn't exist
        log_dir = "./logs"
        os.makedirs(log_dir, exist_ok=True)

        # Create a timestamped log file name within the logs directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_name = os.path.join(log_dir, f"installer_{timestamp}.log")

        # Initialize DockerManager with a placeholder logger (will be set in create_widgets)
        self.logger = None
        self.docker_manager = DockerManager(log_callback=self.log_callback_placeholder)
        
        self.create_widgets()
        
        # Log the starting message and perform initial checks
        self.perform_initial_checks()

    def log_callback_placeholder(self, message, output_mode="both"):
        """Placeholder log callback before the actual logger is set up."""
        pass

    def create_widgets(self):





        # Define consistent padding
        padding = {'padx': 10, 'pady': 5}

        # Header Frame
        header_frame = ttk.Frame(self)
        header_frame.pack(**padding)
        ttk.Label(header_frame, text="Open WebUI Installer", font=("Helvetica", 16)).pack()

        # Info Frame
        info_frame = ttk.LabelFrame(self, text="Information")
        info_frame.pack(fill="both", **padding)
        ttk.Label(info_frame, text="Select a flavor and follow the steps to install Docker and set up containers.").pack(padx=10, pady=5)

        # Main Frame for Docker actions (no padding here)
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Create action buttons side by side
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.install_button = ttk.Button(button_frame, text="Install Docker", command=self.start_docker_installation)
        self.install_button.grid(row=0, column=0, padx=5)
        self.setup_button = ttk.Button(button_frame, text="Set Up Containers", command=self.setup_containers)
        self.setup_button.grid(row=0, column=1, padx=5)
        # self.update_button = ttk.Button(button_frame, text="Update Containers", command=self.update_containers)
        # self.update_button.grid(row=0, column=2, padx=5)

        # Progress Frame, positioned below the Options Panel
        progress_frame = ttk.LabelFrame(main_frame, text="Progress")
        self.logger = Logger(progress_frame, log_file_path=self.log_file_name)

        # Option Panel, visually placed above the "Progress" area
        self.option_panel = OptionPanel(main_frame, log_callback=self.logger.log)
        self.option_panel.pack(fill="both", expand=True, **padding)
        progress_frame.pack(fill="both", expand=True, **padding)
        


  
        
        # Update DockerManager to use the actual logger
        self.docker_manager.log_callback = self.logger.log

        # Initial button states
        self.update_button_states()

    def update_button_states(self):
        """Recheck installation and setup status, and update button states."""
        docker_installed = self.docker_manager.is_docker_installed()
        containers_set_up = docker_installed and self.docker_manager.are_containers_set_up()

        # Enable the install button if Docker is NOT installed, disable it if Docker is installed
        self.install_button.config(state=tk.NORMAL if not docker_installed else tk.DISABLED)

        # Enable the setup button only if Docker is installed and no containers are set up
        self.setup_button.config(state=tk.NORMAL if docker_installed and not containers_set_up else tk.DISABLED)

        # Enable the update button if containers are set up, otherwise disable it
        # self.update_button.config(state=tk.NORMAL if docker_installed and containers_set_up else tk.DISABLED)

        # Additional check for the "watchtower" container to disable the update button
        if self.docker_manager.is_container_present("watchtower"):
            self.update_button.config(state=tk.DISABLED)       

    def perform_initial_checks(self):
        """Run initial Docker check and update button states accordingly."""
        # Log "Running initial Docker check" first

        
        # Perform Docker and container checks
        self.update_button_states()

    def start_docker_installation(self):
        """Install Docker if not present, then update button states."""
        self.install_button.config(state=tk.DISABLED)
        threading.Thread(target=self._install_docker_thread).start()

    def _install_docker_thread(self):
        """Threaded Docker installation to avoid UI freezing."""
        self.logger.log("Starting Docker installation...", output_mode="both")
        self.docker_manager.install_docker()
        
        # Force a re-check of Docker status after installation
        self.docker_manager.reset_docker_status()
        self.update_button_states()
        self.logger.log("Docker installation is complete. Please restart your computer to ensure Docker functions properly.", output_mode="both")
        self.logger.log("After restarting, please open Docker, complete any required account setup, and then restart this installer to proceed.", output_mode="both")

    def setup_containers(self):
        """Run container setup based on selected flavor, then set up the second container, and update button states."""
        # Disable the setup button to prevent additional clicks
        self.setup_button.config(state=tk.DISABLED)

        if self.docker_manager.is_docker_installed():
            flavor_command = self.option_panel.get_selected_flavor_command()
            if flavor_command:
                # Start the main container setup in a separate thread
                threading.Thread(target=self._setup_containers_thread, args=(flavor_command,)).start()
            else:
                # Show warning and re-enable the button if no flavor is selected
                messagebox.showwarning("Selection Needed", "Please select a flavor to set up containers.")
                self.setup_button.config(state=tk.NORMAL)  # Re-enable button if setup was not initiated
        else:
            # Show warning and re-enable the button if Docker is not installed
            messagebox.showwarning("Docker Not Installed", "Please install Docker first.")
            self.setup_button.config(state=tk.NORMAL)  # Re-enable button if setup was not initiated


    def _setup_containers_thread(self, flavor_command):
        """Threaded container setup for both main and secondary containers to avoid UI freezing."""
        """Threaded container setup for watchtower added."""
        self.logger.log("Setting up containers...", output_mode="both")
        self.logger.log("Container [Open WebUI]", output_mode="both")
        # Run the main container first
        self.docker_manager.run_container(flavor_command)
        self.logger.log("Container [Pipeline]", output_mode="both")
        # Run the secondary container after main container setup
        self.docker_manager.run_container(SECONDARY_CONTAINER_COMMAND)
        # Run the watchtower container after pipeline container setup
        self.logger.log("Container [Watchtower]", output_mode="both")
        self.docker_manager.update_containers()

        # Update button states after setting up containers
        self.update_button_states()

    def update_containers(self):
        """Initiate update process for containers in a separate thread to avoid UI freezing."""
        self.update_button.config(state=tk.DISABLED)
        if self.docker_manager.is_docker_installed():
            # Disable the update button temporarily to prevent repeated clicks
            
            threading.Thread(target=self._update_containers_thread).start()
        else:
            self.update_button.config(state=tk.NORMAL)
            messagebox.showwarning("Docker Not Installed", "Please install Docker first.")

    def _update_containers_thread(self):
        """Threaded container update process to avoid UI freezing."""
        self.logger.log("Setting up containers...", output_mode="both")
        self.logger.log("Container [Watchtower]", output_mode="both")
        self.docker_manager.update_containers()
        self.update_button_states()

if __name__ == "__main__":
    app = OpenWebUIInstaller()
    app.mainloop()
