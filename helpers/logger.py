# logger.py
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import logging

class Logger:
    def __init__(self, parent, log_file_path="app.log"):
        """
        Initialize the Logger with options for logging to a text area, file, or both.

        Args:
            parent: The Tkinter parent widget.
            log_file_path (str): Path to the log file for file-based logging.
        """
        self.text_area = ScrolledText(parent, height=10, state="disabled")
        self.text_area.pack(fill="both", expand=True)
        
        # Set up file logging
        self.log_file_path = log_file_path
        logging.basicConfig(
            filename=self.log_file_path,
            filemode="a",  # Append mode
            format="%(asctime)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )

    def log(self, message, output_mode="both"):
        """
        Log a message to the specified output mode (text area, file, or both).

        Args:
            message (str): The message to be logged.
            output_mode (str): "text", "file", or "both" to specify logging output. Defaults to "both".
        """
        # Check if initial messages need to be added to the text area
        if self._is_text_area_empty():
            self._log_to_text_area("Starting Application Checks")
            self._log_to_file("Starting Application Checks")
            self._log_to_text_area("Running initial Docker check.")
            self._log_to_file("Running initial Docker check.")
        
        # Log the actual message to the specified output mode
        if output_mode in {"text", "both"}:
            self._log_to_text_area(message)
        
        if output_mode in {"file", "both"}:
            self._log_to_file(message)
    
    def _log_to_text_area(self, message):
        """Helper to log to the text area."""
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, f"{message}\n")
        self.text_area.see(tk.END)
        self.text_area.config(state="disabled")

    def _log_to_file(self, message):
        """Helper to log to a file."""
        logging.info(message)

    def _is_text_area_empty(self):
        """Check if the text area is empty."""
        return not self.text_area.get("1.0", tk.END).strip()
