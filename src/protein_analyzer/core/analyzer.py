"""Core protein analysis functionality."""

import logging
import time
from typing import List, Optional, Callable

from Bio.SeqRecord import SeqRecord

from ..core.models import (
    AnalysisConfig,
    AnalysisProgress,
    AlphaFoldData,
    NCBIData,
    ProteinData,
)
from ..services.alphafold_service import AlphaFoldService
from ..services.file_service import FileService
from ..services.ncbi_service import NCBIService
from ..shared.exceptions import ProteinAnalyzerError
from ..shared.utils import safe_sleep, validate_record_range

logger = logging.getLogger(__name__)


class ProteinAnalyzer:
    """Main protein analysis orchestrator."""

    def __init__(self):
        """Initialize the protein analyzer with required services."""
        self.ncbi_service = NCBIService()
        self.alphafold_service = AlphaFoldService()
        self.file_service = FileService()

    def analyze_proteins(
        self,
        config: AnalysisConfig,
        progress_callback: Optional[Callable[[AnalysisProgress], None]] = None,
    ) -> str:
        """
        Analyze proteins from a FASTA file and generate results.

        Args:
            config (AnalysisConfig): Analysis configuration.
            progress_callback (Optional[Callable]): Callback for progress updates.

        Returns:
            str: Path to the generated Excel report.

        Raises:
            ProteinAnalyzerError: If analysis fails.
        """
        logger.info("Starting protein analysis pipeline")

        # Validate configuration
        if not config.validate():
            raise ProteinAnalyzerError("Invalid analysis configuration")

        # Initialize progress tracking
        progress = AnalysisProgress()

        try:
            # Read FASTA file
            self._update_progress(
                progress, 0, "Reading FASTA file...", progress_callback
            )
            sequences = self.file_service.read_fasta_file(config.fasta_file_path)
            total_sequences = len(sequences)

            # Validate record range
            end_record = config.end_record or total_sequences
            if not validate_record_range(config.start_record, end_record, total_sequences):
                raise ProteinAnalyzerError(
                    f"Invalid record range: {config.start_record}-{end_record} "
                    f"(total records: {total_sequences})"
                )

            # Filter sequences based on range
            start_idx = config.start_record - 1  # Convert to 0-based index
            end_idx = min(end_record, total_sequences)
            selected_sequences = sequences[start_idx:end_idx]

            progress.total_proteins = len(selected_sequences)
            logger.info(
                f"Processing {progress.total_proteins} proteins "
                f"(records {config.start_record}-{end_idx})"
            )

            # Create output directory
            self.file_service.validate_output_directory(config.output_directory)

            # Process each protein
            all_protein_data = []
            for i, record in enumerate(selected_sequences, 1):
                try:
                    self._update_progress(
                        progress,
                        i,
                        f"Processing protein {i}/{progress.total_proteins}: {record.id}",
                        progress_callback,
                    )

                    protein_data = self._process_single_protein(
                        record, i, config.output_directory
                    )
                    all_protein_data.append(protein_data)

                    # Respectful delay between requests
                    if i < progress.total_proteins:  # Don't sleep after the last protein
                        safe_sleep(config.delay_between_requests)

                except Exception as e:
                    logger.error(f"Error processing protein {record.id}: {e}")
                    # Create error entry for this protein
                    error_data = ProteinData(
                        folder=i,
                        protein_id=record.id,
                        ncbi_description=f"Error: {str(e)}",
                    )
                    all_protein_data.append(error_data)

            # Generate Excel report
            self._update_progress(
                progress, progress.total_proteins, "Generating Excel report...", progress_callback
            )
            excel_path = self.file_service.create_excel_report(
                all_protein_data, config.output_directory
            )

            # Mark as completed
            progress.completed = True
            self._update_progress(
                progress, progress.total_proteins, "Analysis completed!", progress_callback
            )

            logger.info(f"Protein analysis completed. Results: {excel_path}")
            return excel_path

        except Exception as e:
            error_msg = f"Protein analysis failed: {str(e)}"
            logger.error(error_msg)
            progress.error = error_msg
            if progress_callback:
                progress_callback(progress)
            raise ProteinAnalyzerError(error_msg) from e

    def _process_single_protein(
        self, record: SeqRecord, protein_counter: int, output_directory: str
    ) -> ProteinData:
        """
        Process a single protein record.

        Args:
            record (SeqRecord): The protein sequence record.
            protein_counter (int): Counter for folder organization.
            output_directory (str): Base output directory.

        Returns:
            ProteinData: Processed protein data.
        """
        logger.info(f"Processing protein {protein_counter}: {record.id}")

        # Create protein-specific folder
        protein_folder = self.file_service.create_protein_output_folder(
            output_directory, protein_counter
        )

        # Initialize protein data
        protein_data = ProteinData(folder=protein_counter, protein_id=record.id)

        # Fetch NCBI data
        ncbi_data = self.ncbi_service.get_protein_data(record.id)
        protein_data.gene_id = ncbi_data.locus_tag
        protein_data.ncbi_description = ncbi_data.description

        # Fetch AlphaFold data if NCBI data is valid
        if ncbi_data.is_valid:
            alphafold_data = self.alphafold_service.get_protein_data(
                ncbi_data.locus_tag
            )
            self._update_protein_with_alphafold_data(
                protein_data, alphafold_data, protein_folder
            )

        return protein_data

    def _update_protein_with_alphafold_data(
        self,
        protein_data: ProteinData,
        alphafold_data: AlphaFoldData,
        protein_folder: str,
    ) -> None:
        """
        Update protein data with AlphaFold information.

        Args:
            protein_data (ProteinData): Protein data to update.
            alphafold_data (AlphaFoldData): AlphaFold data.
            protein_folder (str): Folder for protein-specific files.
        """
        if not alphafold_data.is_valid:
            logger.warning(f"Invalid AlphaFold data for protein {protein_data.protein_id}")
            return

        protein_data.uniprot_id = alphafold_data.uniprot_id or "Not Found"
        protein_data.aa_length = (
            str(alphafold_data.aa_length) if alphafold_data.aa_length else "N/A"
        )
        protein_data.plddt = (
            str(alphafold_data.plddt) if alphafold_data.plddt else "N/A"
        )
        protein_data.species = alphafold_data.species_classification
        protein_data.alpha_missense = "Yes" if alphafold_data.has_alpha_missense else ""

        # Download PDB file if available
        if alphafold_data.pdb_url and alphafold_data.uniprot_id:
            self.file_service.download_pdb_file(
                alphafold_data.pdb_url, protein_folder, alphafold_data.uniprot_id
            )

    def _update_progress(
        self,
        progress: AnalysisProgress,
        current: int,
        step: str,
        callback: Optional[Callable[[AnalysisProgress], None]],
    ) -> None:
        """
        Update progress and call callback if provided.

        Args:
            progress (AnalysisProgress): Progress object to update.
            current (int): Current progress count.
            step (str): Current step description.
            callback (Optional[Callable]): Progress callback function.
        """
        progress.update(current, step)
        if callback:
            callback(progress)

    def validate_services(self) -> bool:
        """
        Validate that all required services are accessible.

        Returns:
            bool: True if all services are accessible, False otherwise.
        """
        logger.info("Validating service connections...")
        
        ncbi_ok = self.ncbi_service.validate_connection()
        alphafold_ok = self.alphafold_service.validate_connection()
        
        if not ncbi_ok:
            logger.warning("NCBI service validation failed")
        if not alphafold_ok:
            logger.warning("AlphaFold service validation failed")
            
        return ncbi_ok and alphafold_ok

    def get_total_sequences(self, fasta_file_path: str) -> int:
        """
        Get the total number of sequences in a FASTA file.

        Args:
            fasta_file_path (str): Path to the FASTA file.

        Returns:
            int: Number of sequences in the file.

        Raises:
            ProteinAnalyzerError: If the file cannot be read.
        """
        try:
            sequences = self.file_service.read_fasta_file(fasta_file_path)
            return len(sequences)
        except Exception as e:
            raise ProteinAnalyzerError(f"Failed to count sequences: {str(e)}") from e