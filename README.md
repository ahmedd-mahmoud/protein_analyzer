# Protein Analyzer

A Windows desktop application for analyzing protein sequences using NCBI and AlphaFold APIs. This application processes FASTA files and generates comprehensive analysis reports with structural predictions and annotations.

## Features

- **GUI Interface**: User-friendly graphical interface built with tkinter
- **FASTA Processing**: Read and process protein sequences from FASTA files
- **NCBI Integration**: Fetch protein information and locus tags from NCBI database
- **AlphaFold Integration**: Retrieve protein structure predictions and annotations
- **Excel Reports**: Generate formatted Excel reports with analysis results
- **PDB Downloads**: Automatically download PDB structure files
- **Progress Tracking**: Real-time progress updates during analysis
- **Batch Processing**: Process specific ranges of sequences from large FASTA files

## Requirements

- Windows 10 or later
- Python 3.9 or later (for development)
- Internet connection (for API access)

## Installation for Development

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd protein_analyzer
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development tools
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## Usage

1. **Launch the application** by running `python main.py` or using the executable
2. **Select FASTA file** containing protein sequences to analyze
3. **Choose output directory** where results will be saved
4. **Set processing range** (optional):
   - Start Record: First sequence to process (default: 1)
   - End Record: Last sequence to process (default: all)
5. **Configure delay** between API requests (default: 1.0 seconds)
6. **Validate services** to ensure API connectivity (optional)
7. **Count sequences** to verify FASTA file content (optional)
8. **Start analysis** to begin processing

## Output

The application generates:

- **Excel Report** (`analysis_results.xlsx`): Comprehensive analysis results
- **Individual Folders**: Numbered folders for each protein containing PDB files
- **Log File** (`protein_analyzer.log`): Detailed processing logs

### Excel Report Columns

| Column                          | Description                            |
| ------------------------------- | -------------------------------------- |
| Folder                          | Protein folder number                  |
| Protein ID                      | Original protein identifier            |
| Gene ID                         | Locus tag from NCBI                    |
| Uniport ID                      | UniProt accession ID                   |
| AA                              | Amino acid sequence length             |
| PLDDT                           | AlphaFold confidence score             |
| D.ID, D.Z SCORE, D.RMSD, D.NAME | DALI results (manual entry)            |
| M.ID, M.IM, M.RSMD, M.NAME      | MTM results (manual entry)             |
| Interpro                        | InterPro annotations (manual entry)    |
| NCBI                            | Protein description from NCBI          |
| PDB E.value                     | E-value from AlphaFold (manual entry)  |
| Species                         | Species specificity (General/Specific) |
| Alpha missense                  | Alpha Missense availability            |

## Configuration

The application uses several configuration files:

- `requirements.txt`: Core dependencies
- `requirements-dev.txt`: Development dependencies
- `pyproject.toml`: Tool configurations (Black, isort, pytest, etc.)

## Development

### Code Quality Tools

The project uses several tools to maintain code quality:

```bash
# Format code
black src/

# Sort imports
isort src/

# Lint code
flake8 src/

# Type checking
mypy src/

# Security scanning
bandit -r src/

# Run tests
pytest
```

### Project Structure

```
protein_analyzer/
├── src/
│   └── protein_analyzer/
│       ├── gui/              # GUI components
│       ├── core/             # Core analysis logic
│       ├── services/         # API services
│       ├── shared/           # Shared utilities
│       └── tests/            # Unit tests
├── main.py                   # Application entry point
├── requirements.txt          # Dependencies
└── README.md                # This file
```

## API Services

### NCBI E-utilities

- Fetches protein information and locus tags
- Uses GenBank format data retrieval
- Handles rate limiting and error recovery

### AlphaFold Database

- Searches for UniProt IDs using locus tags
- Retrieves structure predictions and confidence scores
- Downloads PDB files for structural analysis
- Accesses clustering information for species classification
