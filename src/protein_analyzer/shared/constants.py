"""Shared constants for the Protein Analyzer application."""

# API Endpoints
NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
ALPHAFOLD_SEARCH_URL = "https://alphafold.ebi.ac.uk/api/search"
ALPHAFOLD_PREDICTION_URL = "https://alphafold.ebi.ac.uk/api/prediction"
ALPHAFOLD_CLUSTER_URL = "https://alphafold.ebi.ac.uk/api/cluster/members"

# Default values
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_REQUEST_DELAY_SECONDS = 1
DEFAULT_CHUNK_SIZE = 8192

# Species classification thresholds
GENERAL_SPECIES_THRESHOLD = 100
SPECIFIC_SPECIES_THRESHOLD = 10

# PLDDT threshold for highlighting
PLDDT_HIGHLIGHT_THRESHOLD = 70

# Column ordering for Excel output
EXCEL_COLUMN_ORDER = [
    "Folder",
    "Protein ID",
    "Gene ID",
    "Uniport ID",
    "AA",
    "PLDDT",
    "D.ID",
    "D.Z SCORE",
    "D.RMSD",
    "D.NAME",
    "M.ID",
    "M.IM",
    "M.RSMD",
    "M.NAME",
    "Interpro",
    "NCBI",
    "PDB E.value",
    "Species",
    "Alpha missense",
]

# File extensions
FASTA_EXTENSIONS = [".fasta", ".fa", ".fas", ".seq"]
EXCEL_EXTENSION = ".xlsx"
PDB_EXTENSION = ".pdb"

# Default output filename
DEFAULT_OUTPUT_FILENAME = "analysis_results.xlsx"