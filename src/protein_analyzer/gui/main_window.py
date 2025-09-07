"""Main GUI window for the Protein Analyzer application."""

import logging
import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import tkinter as tk
from tkinter import ttk

from ..core.analyzer import ProteinAnalyzer
from ..core.models import AnalysisConfig, AnalysisProgress
from ..shared.exceptions import ProteinAnalyzerError
from ..shared.utils import validate_fasta_file, validate_output_directory
from .progress_dialog import ProgressDialog

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window."""

    def __init__(self):
        """Initialize the main window."""
        self.root = tk.Tk()
        self.root.title("Protein Analyzer")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Initialize analyzer
        self.analyzer = ProteinAnalyzer()
        
        # Initialize variables
        self.fasta_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.start_record_var = tk.StringVar(value="1")
        self.end_record_var = tk.StringVar()
        self.delay_var = tk.StringVar(value="1.0")
        
        # Progress dialog reference
        self.progress_dialog: Optional[ProgressDialog] = None
        
        # Analysis thread reference
        self.analysis_thread: Optional[threading.Thread] = None
        
        self._setup_ui()
        self._setup_logging_display()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(5, weight=1)  # Log area row

        # Title
        title_label = tk.Label(
            self.root,
            text="Protein Analyzer",
            font=("Arial", 16, "bold"),
            pady=10
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Main frame for inputs
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20)
        main_frame.grid_columnconfigure(1, weight=1)

        # FASTA file selection
        ttk.Label(main_frame, text="FASTA File:").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )
        fasta_frame = ttk.Frame(main_frame)
        fasta_frame.grid(row=0, column=1, sticky="ew", pady=(0, 10))
        fasta_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Entry(fasta_frame, textvariable=self.fasta_file_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 10)
        )
        ttk.Button(
            fasta_frame, text="Browse", command=self._browse_fasta_file
        ).grid(row=0, column=1)

        # Output directory selection
        ttk.Label(main_frame, text="Output Directory:").grid(
            row=1, column=0, sticky="w", pady=(0, 10)
        )
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=1, column=1, sticky="ew", pady=(0, 10))
        output_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_dir_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 10)
        )
        ttk.Button(
            output_frame, text="Browse", command=self._browse_output_directory
        ).grid(row=0, column=1)

        # Record range
        range_frame = ttk.Frame(main_frame)
        range_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        ttk.Label(range_frame, text="Start Record:").grid(row=0, column=0, sticky="w")
        start_entry = ttk.Entry(range_frame, textvariable=self.start_record_var, width=10)
        start_entry.grid(row=0, column=1, padx=(10, 20), sticky="w")
        
        ttk.Label(range_frame, text="End Record:").grid(row=0, column=2, sticky="w")
        end_entry = ttk.Entry(range_frame, textvariable=self.end_record_var, width=10)
        end_entry.grid(row=0, column=3, padx=(10, 20), sticky="w")
        
        ttk.Label(range_frame, text="(Leave end empty for all records)").grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(5, 0)
        )

        # Request delay
        ttk.Label(main_frame, text="Delay Between Requests (seconds):").grid(
            row=3, column=0, sticky="w", pady=(0, 10)
        )
        delay_entry = ttk.Entry(main_frame, textvariable=self.delay_var, width=10)
        delay_entry.grid(row=3, column=1, sticky="w", pady=(0, 10))

        # Buttons frame
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        # Validate services button
        ttk.Button(
            button_frame,
            text="Validate Services",
            command=self._validate_services
        ).grid(row=0, column=0, padx=(0, 10))

        # Count sequences button
        ttk.Button(
            button_frame,
            text="Count Sequences",
            command=self._count_sequences
        ).grid(row=0, column=1, padx=(0, 10))

        # Start analysis button
        self.start_button = ttk.Button(
            button_frame,
            text="Start Analysis",
            command=self._start_analysis
        )
        self.start_button.grid(row=0, column=2)

        # Status frame
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20)
        status_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky="w")
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=1, sticky="w", padx=(10, 0))

        # Separator
        ttk.Separator(self.root, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=10
        )

    def _setup_logging_display(self) -> None:
        """Set up the logging display area."""
        log_frame = ttk.LabelFrame(self.root, text="Log Output", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 20))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)

        # Text widget with scrollbar
        self.log_text = tk.Text(log_frame, height=8, state="disabled", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Clear log button
        ttk.Button(log_frame, text="Clear Log", command=self._clear_log).grid(
            row=1, column=0, columnspan=2, pady=(10, 0)
        )

    def _browse_fasta_file(self) -> None:
        """Open file browser for FASTA file selection."""
        file_path = filedialog.askopenfilename(
            title="Select FASTA File",
            filetypes=[
                ("FASTA files", "*.fasta *.fa *.fas *.seq"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.fasta_file_var.set(file_path)
            self._log_message(f"Selected FASTA file: {file_path}")

    def _browse_output_directory(self) -> None:
        """Open directory browser for output directory selection."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
            self._log_message(f"Selected output directory: {directory}")

    def _validate_services(self) -> None:
        """Validate that external services are accessible."""
        self._update_status("Validating services...")
        self._log_message("Validating external services...")
        
        def validate_in_background():
            try:
                result = self.analyzer.validate_services()
                
                self.root.after(0, lambda: self._handle_validation_result(result))
            except Exception as e:
                self.root.after(0, lambda: self._handle_validation_error(str(e)))
        
        # Run validation in background thread
        threading.Thread(target=validate_in_background, daemon=True).start()

    def _handle_validation_result(self, result: bool) -> None:
        """Handle the result of service validation."""
        if result:
            self._update_status("Services validated successfully")
            self._log_message("All external services are accessible")
            messagebox.showinfo("Validation", "All services are accessible!")
        else:
            self._update_status("Service validation failed")
            self._log_message("Some external services are not accessible")
            messagebox.showwarning(
                "Validation", 
                "Some services are not accessible. Check your internet connection."
            )

    def _handle_validation_error(self, error_msg: str) -> None:
        """Handle validation error."""
        self._update_status("Validation error")
        self._log_message(f"Validation error: {error_msg}")
        messagebox.showerror("Error", f"Validation failed: {error_msg}")

    def _count_sequences(self) -> None:
        """Count sequences in the selected FASTA file."""
        fasta_file = self.fasta_file_var.get().strip()
        
        if not fasta_file:
            messagebox.showwarning("Warning", "Please select a FASTA file first.")
            return
            
        if not validate_fasta_file(fasta_file):
            messagebox.showerror("Error", "Invalid FASTA file. Please check the file path.")
            return

        self._update_status("Counting sequences...")
        
        def count_in_background():
            try:
                count = self.analyzer.get_total_sequences(fasta_file)
                self.root.after(0, lambda: self._handle_sequence_count(count))
            except Exception as e:
                self.root.after(0, lambda: self._handle_count_error(str(e)))
        
        threading.Thread(target=count_in_background, daemon=True).start()

    def _handle_sequence_count(self, count: int) -> None:
        """Handle the result of sequence counting."""
        self._update_status(f"Found {count} sequences")
        self._log_message(f"FASTA file contains {count} sequences")
        
        # Update end record if not set
        if not self.end_record_var.get().strip():
            self.end_record_var.set(str(count))
        
        messagebox.showinfo("Sequence Count", f"Found {count} sequences in the FASTA file.")

    def _handle_count_error(self, error_msg: str) -> None:
        """Handle sequence counting error."""
        self._update_status("Error counting sequences")
        self._log_message(f"Error counting sequences: {error_msg}")
        messagebox.showerror("Error", f"Failed to count sequences: {error_msg}")

    def _start_analysis(self) -> None:
        """Start the protein analysis process."""
        if self.analysis_thread and self.analysis_thread.is_alive():
            messagebox.showwarning("Warning", "Analysis is already running.")
            return

        # Validate inputs
        config = self._create_analysis_config()
        if not config:
            return

        # Disable the start button
        self.start_button.config(state="disabled")
        
        # Create and show progress dialog
        self.progress_dialog = ProgressDialog(self.root, self._cancel_analysis)
        
        # Start analysis in background thread
        self.analysis_thread = threading.Thread(
            target=self._run_analysis, args=(config,), daemon=True
        )
        self.analysis_thread.start()

    def _create_analysis_config(self) -> Optional[AnalysisConfig]:
        """
        Create and validate analysis configuration from GUI inputs.
        
        Returns:
            Optional[AnalysisConfig]: Valid config or None if validation fails.
        """
        # Get values from GUI
        fasta_file = self.fasta_file_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        start_record_str = self.start_record_var.get().strip()
        end_record_str = self.end_record_var.get().strip()
        delay_str = self.delay_var.get().strip()

        # Validate inputs
        if not fasta_file:
            messagebox.showerror("Error", "Please select a FASTA file.")
            return None

        if not validate_fasta_file(fasta_file):
            messagebox.showerror("Error", "Invalid FASTA file. Please check the file path.")
            return None

        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return None

        if not validate_output_directory(output_dir):
            messagebox.showerror("Error", "Invalid output directory. Please check the path.")
            return None

        # Parse numeric values
        try:
            start_record = int(start_record_str) if start_record_str else 1
            end_record = int(end_record_str) if end_record_str else None
            delay = float(delay_str) if delay_str else 1.0
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values. Please check your inputs.")
            return None

        # Validate ranges
        if start_record < 1:
            messagebox.showerror("Error", "Start record must be at least 1.")
            return None

        if end_record is not None and end_record < start_record:
            messagebox.showerror("Error", "End record must be greater than or equal to start record.")
            return None

        if delay < 0:
            messagebox.showerror("Error", "Delay must be non-negative.")
            return None

        return AnalysisConfig(
            fasta_file_path=fasta_file,
            output_directory=output_dir,
            start_record=start_record,
            end_record=end_record,
            delay_between_requests=delay,
        )

    def _run_analysis(self, config: AnalysisConfig) -> None:
        """
        Run the protein analysis in a background thread.
        
        Args:
            config (AnalysisConfig): Analysis configuration.
        """
        try:
            self.root.after(0, lambda: self._update_status("Starting analysis..."))
            
            # Run analysis with progress callback
            result_path = self.analyzer.analyze_proteins(
                config, self._progress_callback
            )
            
            # Analysis completed successfully
            self.root.after(0, lambda: self._handle_analysis_complete(result_path))
            
        except Exception as e:
            # Analysis failed
            self.root.after(0, lambda: self._handle_analysis_error(str(e)))

    def _progress_callback(self, progress: AnalysisProgress) -> None:
        """
        Callback function for analysis progress updates.
        
        Args:
            progress (AnalysisProgress): Current progress information.
        """
        # Schedule GUI update in main thread
        self.root.after(0, lambda: self._update_progress_gui(progress))

    def _update_progress_gui(self, progress: AnalysisProgress) -> None:
        """
        Update the progress dialog and status.
        
        Args:
            progress (AnalysisProgress): Current progress information.
        """
        if self.progress_dialog:
            self.progress_dialog.update_progress(progress)
        
        self._update_status(progress.current_step)
        self._log_message(progress.current_step)

    def _handle_analysis_complete(self, result_path: str) -> None:
        """Handle successful completion of analysis."""
        self._update_status("Analysis completed successfully")
        self._log_message(f"Analysis completed. Results saved to: {result_path}")
        
        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        # Re-enable start button
        self.start_button.config(state="normal")
        
        # Show completion message with better formatting
        output_dir = os.path.dirname(result_path)
        result = messagebox.askyesno(
            "Analysis Complete",
            f"Analysis completed successfully!\n\n"
            f"Results saved to:\n{result_path}\n\n"
            f"Output directory:\n{output_dir}\n\n"
            f"Would you like to open the output directory?"
        )
        
        if result:
            self._open_output_directory(output_dir)

    def _handle_analysis_error(self, error_msg: str) -> None:
        """Handle analysis error."""
        self._update_status("Analysis failed")
        self._log_message(f"Analysis failed: {error_msg}")
        
        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        # Re-enable start button
        self.start_button.config(state="normal")
        
        # Show error message
        messagebox.showerror("Analysis Failed", f"Analysis failed with error:\n\n{error_msg}")

    def _cancel_analysis(self) -> None:
        """Cancel the running analysis."""
        # Note: Python threads cannot be forcefully terminated
        # This is a limitation we acknowledge
        self._update_status("Analysis cancellation requested")
        self._log_message("Analysis cancellation requested (will complete current protein)")
        
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        self.start_button.config(state="normal")

    def _open_output_directory(self, directory: str) -> None:
        """
        Open the output directory in the system file explorer.
        
        Args:
            directory (str): Directory path to open.
        """
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                os.startfile(directory)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", directory])
            else:  # Linux and others
                subprocess.run(["xdg-open", directory])
                
        except Exception as e:
            self._log_message(f"Failed to open directory: {e}")
            messagebox.showwarning(
                "Cannot Open Directory", 
                f"Could not open the output directory automatically.\n\nPath: {directory}"
            )

    def _update_status(self, status: str) -> None:
        """
        Update the status label.
        
        Args:
            status (str): New status text.
        """
        self.status_label.config(text=status)

    def _log_message(self, message: str) -> None:
        """
        Add a message to the log display.
        
        Args:
            message (str): Message to log.
        """
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _clear_log(self) -> None:
        """Clear the log display."""
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def run(self) -> None:
        """Start the GUI application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application terminated by user")
        except Exception as e:
            logger.error(f"Unexpected error in GUI: {e}")
            messagebox.showerror("Fatal Error", f"An unexpected error occurred: {e}")

    def cleanup(self) -> None:
        """Clean up resources before closing."""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        # Note: We cannot forcefully stop background threads in Python
        # They will complete naturally when the process exits