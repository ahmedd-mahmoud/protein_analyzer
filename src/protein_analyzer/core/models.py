"""Data models for the Protein Analyzer application."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ProteinData:
    """Data model representing a protein and its analysis results."""

    folder: int
    protein_id: str
    gene_id: str = "Not Found"
    uniprot_id: str = "Not Found"
    aa_length: str = "N/A"
    plddt: str = "N/A"
    d_id: str = ""
    d_z_score: str = ""
    d_rmsd: str = ""
    d_name: str = ""
    m_id: str = ""
    m_im: str = ""
    m_rsmd: str = ""
    m_name: str = ""
    interpro: str = "MANUAL ENTRY: Run InterProScan and summarize results here."
    ncbi_description: str = "Not Found"
    pdb_e_value: str = "MANUAL ENTRY: From AlphaFold website."
    species: str = ""
    alpha_missense: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ProteinData object to a dictionary for Excel export.

        Returns:
            Dict[str, Any]: Dictionary representation of the protein data.
        """
        return {
            "Folder": self.folder,
            "Protein ID": self.protein_id,
            "Gene ID": self.gene_id,
            "Uniport ID": self.uniprot_id,
            "AA": self.aa_length,
            "PLDDT": self.plddt,
            "D.ID": self.d_id,
            "D.Z SCORE": self.d_z_score,
            "D.RMSD": self.d_rmsd,
            "D.NAME": self.d_name,
            "M.ID": self.m_id,
            "M.IM": self.m_im,
            "M.RSMD": self.m_rsmd,
            "M.NAME": self.m_name,
            "Interpro": self.interpro,
            "NCBI": self.ncbi_description,
            "PDB E.value": self.pdb_e_value,
            "Species": self.species,
            "Alpha missense": self.alpha_missense,
        }


@dataclass
class NCBIData:
    """Data model for NCBI protein information."""

    locus_tag: str
    description: str
    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        """Check if the NCBI data is valid and complete."""
        return (
            self.error is None
            and self.locus_tag not in ["Not Found", "Error"]
            and self.description not in ["Not Found", "Error"]
        )


@dataclass
class AlphaFoldData:
    """Data model for AlphaFold prediction information."""

    uniprot_id: Optional[str] = None
    aa_length: Optional[int] = None
    plddt: Optional[float] = None
    pdb_url: Optional[str] = None
    similar_proteins_count: Optional[int] = None
    has_alpha_missense: bool = False
    error: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if the AlphaFold data is valid and complete."""
        return self.error is None and self.uniprot_id is not None

    @property
    def species_classification(self) -> str:
        """
        Classify species based on similar proteins count.

        Returns:
            str: Species classification ("General", "Specific", or empty string).
        """
        if self.similar_proteins_count is None:
            return ""

        from ..shared.constants import GENERAL_SPECIES_THRESHOLD, SPECIFIC_SPECIES_THRESHOLD

        if self.similar_proteins_count >= GENERAL_SPECIES_THRESHOLD:
            return "General"
        elif self.similar_proteins_count < SPECIFIC_SPECIES_THRESHOLD:
            return "Specific"
        else:
            return ""


@dataclass
class AnalysisConfig:
    """Configuration for protein analysis."""

    fasta_file_path: str
    output_directory: str
    start_record: int = 1
    end_record: Optional[int] = None
    delay_between_requests: float = 1.0

    def validate(self) -> bool:
        """
        Validate the analysis configuration.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        from ..shared.utils import validate_fasta_file, validate_output_directory

        if not validate_fasta_file(self.fasta_file_path):
            return False

        if not validate_output_directory(self.output_directory):
            return False

        if self.start_record < 1:
            return False

        if self.end_record is not None and self.end_record < self.start_record:
            return False

        return True


@dataclass
class AnalysisProgress:
    """Model for tracking analysis progress."""

    current_protein: int = 0
    total_proteins: int = 0
    current_step: str = ""
    completed: bool = False
    error: Optional[str] = None

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_proteins == 0:
            return 0.0
        return min(100.0, (self.current_protein / self.total_proteins) * 100.0)

    def update(self, current: int, step: str) -> None:
        """Update progress information."""
        self.current_protein = current
        self.current_step = step