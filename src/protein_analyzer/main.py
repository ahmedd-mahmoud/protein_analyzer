"""Main entry point for the Protein Analyzer application."""

import logging
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from protein_analyzer.gui.main_window import MainWindow
from protein_analyzer.shared.exceptions import ProteinAnalyzerError


def setup_logging() -> None:
    """Set up logging configuration for the application."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("protein_analyzer.log", mode="a"),
        ],
    )
    
    # Set specific log levels for external libraries
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def main() -> None:
    """Main function to start the application."""
    try:
        # Set up logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting Protein Analyzer application")
        
        # Create and run the main window
        app = MainWindow()
        app.run()
        
        # Clean up
        app.cleanup()
        logger.info("Application closed normally")
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except ProteinAnalyzerError as e:
        print(f"Application error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.exception("Unexpected error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()