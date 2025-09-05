import os
import re
import time
import requests
import pandas as pd
from Bio import SeqIO

# --- FUNCTIONS TO FETCH DATA FROM WEB APIs ---

def get_ncbi_data(protein_id):
    """Fetches the locus tag and protein description from NCBI."""
    print(f"  -> Querying NCBI for protein ID: {protein_id}")
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "protein",
        "id": protein_id,
        "rettype": "gb",
        "retmode": "text"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        content = response.text

        # Use regular expressions to find the locus_tag
        locus_tag_match = re.search(r'/locus_tag="([^"]+)"', content)
        locus_tag = locus_tag_match.group(1) if locus_tag_match else "Not Found"

        # Find the definition (protein name)
        definition_match = re.search(r"DEFINITION\s+(.+)", content)
        definition = definition_match.group(1).strip() if definition_match else "Not Found"
        
        return locus_tag, definition
    except requests.exceptions.RequestException as e:
        print(f"    [ERROR] Could not fetch data from NCBI for {protein_id}. Error: {e}")
        return "Error", "Error"

def get_uniprot_id_from_locus_tag(locus_tag):
    """Maps a locus tag to a UniProt ID using the UniProt mapping service."""
    print(f"  -> Querying UniProt for Locus Tag: {locus_tag}")
    url = "https://rest.uniprot.org/idmapping/run"
    params = {
        "from": "Gene_Locus",
        "to": "UniProtKB",
        "ids": locus_tag
    }
    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
        job_id = response.json().get("jobId")

        if not job_id:
            return "Not Found"

        # Poll for results
        while True:
            status_url = f"https://rest.uniprot.org/idmapping/status/{job_id}"
            status_response = requests.get(status_url)
            status_response.raise_for_status()
            status_data = status_response.json()
            if "results" in status_data or "jobStatus" in status_data and status_data["jobStatus"] != "RUNNING":
                break
            time.sleep(2) # Wait before checking again

        results_url = f"https://rest.uniprot.org/idmapping/results/{job_id}"
        results_response = requests.get(results_url)
        results_response.raise_for_status()
        results = results_response.json().get("results", [])

        if results and "to" in results[0]:
            return results[0]["to"]
        return "Not Found"
        
    except requests.exceptions.RequestException as e:
        print(f"    [ERROR] Could not map locus tag {locus_tag} to UniProt ID. Error: {e}")
        return "Error"


def get_alphafold_data(uniprot_id):
    """Fetches key data from the AlphaFold API using a UniProt ID."""
    if not uniprot_id or uniprot_id in ["Not Found", "Error"]:
        return None
    print(f"  -> Querying AlphaFold for UniProt ID: {uniprot_id}")
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()[0]  # The API returns a list, we want the first (and only) item
        else:
            print(f"    [INFO] No AlphaFold entry found for {uniprot_id} (Status code: {response.status_code})")
            return None
    except requests.exceptions.RequestException as e:
        print(f"    [ERROR] Could not fetch data from AlphaFold for {uniprot_id}. Error: {e}")
        return None

def download_file(url, save_path):
    """Downloads a file from a URL to a specified path."""
    try:
        print(f"  -> Downloading file from: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"    -> Successfully saved to: {os.path.basename(save_path)}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"    [ERROR] Failed to download file. Error: {e}")
        return False

# --- MAIN SCRIPT ---

def main():
    """Main function to run the analysis pipeline."""
    # --- 1. SETUP YOUR FILE PATHS HERE ---
    # IMPORTANT: Use forward slashes '/' in your paths, even on Windows.
    fasta_input_file = "D:/Career Learning/Randoms/file.fasta"
    main_output_directory = "D:/Career Learning/Randoms/output"

    print("--- Starting Protein Analysis Pipeline ---")

    # --- 2. PREPARE OUTPUT DIRECTORY AND DATA STORAGE ---
    os.makedirs(main_output_directory, exist_ok=True)
    all_proteins_data = []
    protein_counter = 0

    # --- 3. PARSE FASTA FILE AND PROCESS EACH PROTEIN ---
    try:
        fasta_sequences = list(SeqIO.parse(fasta_input_file, "fasta"))
        print(f"Found {len(fasta_sequences)} proteins in the FASTA file.")
    except FileNotFoundError:
        print(f"[FATAL ERROR] The input FASTA file was not found at: {fasta_input_file}")
        print("Please check the path and try again.")
        return

    for record in fasta_sequences:
        protein_counter += 1
        protein_id = record.id
        print(f"\n--- Processing Protein {protein_counter}/{len(fasta_sequences)}: {protein_id} ---")

        # Create a dedicated folder for this protein's files
        protein_folder_path = os.path.join(main_output_directory, str(protein_counter))
        os.makedirs(protein_folder_path, exist_ok=True)

        # --- 4. AUTOMATED DATA FETCHING ---
        locus_tag, ncbi_protein_name = get_ncbi_data(protein_id)
        
        uniprot_id = "Not Found"
        if locus_tag not in ["Not Found", "Error"]:
            uniprot_id = get_uniprot_id_from_locus_tag(locus_tag)
        
        # Initialize AlphaFold data with default values
        aa_length = 'N/A'
        plddt = 'N/A'

        af_data = get_alphafold_data(uniprot_id)
        if af_data:
            aa_length = af_data.get('uniprotSequenceLength', 'N/A')
            plddt = af_data.get('plddt', 'N/A')
            pdb_url = af_data.get('pdbUrl')

            # Download the PDB file if a URL was found
            if pdb_url:
                pdb_filename = f"{uniprot_id}.pdb"
                pdb_save_path = os.path.join(protein_folder_path, pdb_filename)
                download_file(pdb_url, pdb_save_path)
        
        # --- 5. STORE ALL COLLECTED DATA ---
        # Data for DALI, MTM, Interpro etc. are placeholders for you to fill in manually.
        protein_data = {
            'Folder': protein_counter,
            'Protein ID': protein_id,
            'Gene ID': locus_tag,
            'Uniport ID': uniprot_id,
            'AA': aa_length,
            'PLDDT': plddt,
            'D.ID': '',
            'D.Z SCORE': '',
            'D.RMSD': '',
            'D.NAME': '',
            'M.ID': '',
            'M.IM': '',
            'M.RSMD': '',
            'M.NAME': '',
            'Interpro': 'MANUAL ENTRY: Run InterProScan and summarize results here.',
            'NCBI': ncbi_protein_name,
            'PDB E.value': 'MANUAL ENTRY: From AlphaFold website.',
            'Species': 'MANUAL ENTRY: From AlphaFold website.',
            'Alpha missense': 'MANUAL ENTRY: From AlphaFold website.'
        }
        all_proteins_data.append(protein_data)
        
        # A short delay to be respectful to the servers
        time.sleep(1)

    # --- 6. CREATE AND SAVE THE EXCEL FILE ---
    print("\n--- All proteins processed. Generating Excel report... ---")
    df = pd.DataFrame(all_proteins_data)

    # Reorder columns to match your example
    column_order = [
        'Folder', 'Protein ID', 'Gene ID', 'Uniport ID', 'AA', 'PLDDT',
        'D.ID', 'D.Z SCORE', 'D.RMSD', 'D.NAME', 'M.ID', 'M.IM', 'M.RSMD',
        'M.NAME', 'Interpro', 'NCBI', 'PDB E.value', 'Species', 'Alpha missense'
    ]
    df = df[column_order]

    excel_output_path = os.path.join(main_output_directory, "analysis_results.xlsx")
    df.to_excel(excel_output_path, index=False)

    print(f"--- Pipeline Finished! ---")
    print(f"Results saved to: {excel_output_path}")
    print(f"PDB files and other data are organized in numbered folders inside: {main_output_directory}")

if __name__ == "__main__":
    main()