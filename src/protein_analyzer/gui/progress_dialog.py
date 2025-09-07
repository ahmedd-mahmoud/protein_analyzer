"""Progress dialog for displaying analysis progress."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from ..core.models import AnalysisProgress


class ProgressDialog:
    """Dialog window for showing analysis progress."""

    def __init__(self, parent: tk.Tk, cancel_callback: Optional[Callable] = None):
        """
        Initialize the progress dialog.

        Args:
            parent (tk.Tk): Parent window.
            cancel_callback (Optional[Callable]): Callback for cancel button.
        """
        self.parent = parent
        self.cancel_callback = cancel_callback
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Analysis Progress")
        self.dialog.geometry("500x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Prevent closing with X button (use cancel button instead)
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._setup_ui()

    def _center_dialog(self) -> None:
        """Center the dialog window on the parent."""
        self.dialog.update_idletasks()
        
        # Get parent position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        # Calculate position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    def _setup_ui(self) -> None:
        """Set up the dialog user interface."""
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Analyzing Proteins...",
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Progress information frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", pady=(0, 10))

        # Current step label
        ttk.Label(info_frame, text="Current Step:").pack(anchor="w")
        self.step_label = ttk.Label(info_frame, text="Initializing...")
        self.step_label.pack(anchor="w", pady=(5, 10))

        # Progress bar
        ttk.Label(info_frame, text="Progress:").pack(anchor="w")
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            info_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(fill="x", pady=(5, 10))

        # Progress percentage label
        self.percentage_label = ttk.Label(info_frame, text="0%")
        self.percentage_label.pack(anchor="w")

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))

        # Cancel button
        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        )
        self.cancel_button.pack(side="right")

        # Note about cancellation
        note_label = ttk.Label(
            button_frame,
            text="Note: Cancellation will complete the current protein before stopping.",
            font=("Arial", 8),
            foreground="gray"
        )
        note_label.pack(side="left")

    def update_progress(self, progress: AnalysisProgress) -> None:
        """
        Update the progress display.

        Args:
            progress (AnalysisProgress): Current progress information.
        """
        # Update step description
        self.step_label.config(text=progress.current_step)
        
        # Update progress bar and percentage
        percentage = progress.progress_percentage
        self.progress_var.set(percentage)
        self.percentage_label.config(text=f"{percentage:.1f}%")
        
        # If completed, close the dialog
        if progress.completed and not progress.error:
            self.dialog.after(1000, self.close)  # Close after 1 second
        elif progress.error:
            # Show error and enable close
            self.step_label.config(text=f"Error: {progress.error}")
            self.cancel_button.config(text="Close")

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        if self.cancel_callback:
            self.cancel_callback()
        else:
            self.close()

    def _on_close(self) -> None:
        """Handle dialog close attempt."""
        # Prevent closing with X button, use cancel instead
        self._on_cancel()

    def close(self) -> None:
        """Close the progress dialog."""
        try:
            self.dialog.grab_release()
            self.dialog.destroy()
        except tk.TclError:
            # Dialog already destroyed
            pass

    def is_open(self) -> bool:
        """
        Check if the dialog is still open.

        Returns:
            bool: True if dialog is open, False otherwise.
        """
        try:
            return self.dialog.winfo_exists()
        except tk.TclError:
            return False