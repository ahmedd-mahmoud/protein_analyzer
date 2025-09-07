"""Service for interacting with AlphaFold API."""

import json
import logging
from typing import Optional, Tuple

import requests

from ..core.models import AlphaFoldData
from ..shared.constants import (
    ALPHAFOLD_SEARCH_URL,
    ALPHAFOLD_PREDICTION_URL,
    ALPHAFOLD_CLUSTER_URL,
    DEFAULT_TIMEOUT_SECONDS,
)
from ..shared.exceptions import AlphaFoldError

logger = logging.getLogger(__name__)


class AlphaFoldService:
    """Service for fetching protein structure data from AlphaFold."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        """
        Initialize the AlphaFold service.

        Args:
            timeout (int): Request timeout in seconds.
        """
        self.timeout = timeout

    def get_protein_data(self, locus_tag: str) -> AlphaFoldData:
        """
        Fetch protein structure data from AlphaFold using locus tag.

        This method performs a two-step process:
        1. Search for the locus tag to find the corresponding UniProt ID
        2. Fetch the prediction data using the UniProt ID

        Args:
            locus_tag (str): The locus tag to search for.

        Returns:
            AlphaFoldData: Object containing the fetched data or error information.
        """
        if not locus_tag or not locus_tag.strip() or locus_tag.strip() in ["Not Found", "Error"]:
            return AlphaFoldData(error="Invalid locus tag provided")

        locus_tag = locus_tag.strip()
        logger.info(f"Processing AlphaFold data for locus tag: {locus_tag}")

        # Step 1: Search for UniProt ID
        uniprot_id = self._search_uniprot_id(locus_tag)
        if not uniprot_id:
            logger.info(f"No UniProt ID found for locus tag: {locus_tag}")
            return AlphaFoldData(error="UniProt ID not found for locus tag")

        # Step 2: Get prediction data
        prediction_data = self._get_prediction_data(uniprot_id)
        if not prediction_data:
            logger.info(f"No prediction data found for UniProt ID: {uniprot_id}")
            return AlphaFoldData(
                uniprot_id=uniprot_id, error="Prediction data not found"
            )

        # Step 3: Get cluster information
        similar_proteins_count = self._get_similar_proteins_count(uniprot_id)

        # Parse the prediction data
        return self._parse_prediction_data(
            prediction_data, uniprot_id, similar_proteins_count
        )

    def _search_uniprot_id(self, locus_tag: str) -> Optional[str]:
        """
        Search AlphaFold for a UniProt ID using a locus tag.

        Args:
            locus_tag (str): The locus tag to search for.

        Returns:
            Optional[str]: The UniProt ID if found, None otherwise.
        """
        logger.info(f"Searching AlphaFold for locus tag: '{locus_tag}'")

        params = {
            "q": f"(text:*{locus_tag} OR text:{locus_tag}*)",
            "type": "main",
            "start": 0,
            "rows": 20,
        }

        try:
            response = requests.get(
                ALPHAFOLD_SEARCH_URL, params=params, timeout=self.timeout
            )
            response.raise_for_status()

            search_results = response.json()

            if not search_results.get("docs"):
                logger.info(f"No search results found for locus tag '{locus_tag}'")
                return None

            # Take the first hit as the most relevant
            first_hit = search_results["docs"][0]
            uniprot_id = first_hit.get("uniprotAccession")

            if uniprot_id:
                logger.info(f"Found corresponding UniProt ID: {uniprot_id}")
                return uniprot_id
            else:
                logger.warning(
                    f"Search successful but could not extract UniProt ID for '{locus_tag}'"
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search AlphaFold for '{locus_tag}': {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response for '{locus_tag}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during AlphaFold search for '{locus_tag}': {e}")
            return None

    def _get_prediction_data(self, uniprot_id: str) -> Optional[dict]:
        """
        Fetch prediction data from AlphaFold using UniProt ID.

        Args:
            uniprot_id (str): The UniProt ID to fetch data for.

        Returns:
            Optional[dict]: The prediction data if found, None otherwise.
        """
        logger.info(f"Querying AlphaFold for prediction data for {uniprot_id}")

        prediction_url = f"{ALPHAFOLD_PREDICTION_URL}/{uniprot_id}"

        try:
            response = requests.get(prediction_url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    logger.info(f"AlphaFold data retrieved successfully for {uniprot_id}")
                    return data[0]  # API returns a list, we want the first item
                else:
                    logger.warning(f"Empty or invalid prediction data for {uniprot_id}")
                    return None
            else:
                logger.info(
                    f"No AlphaFold entry found for {uniprot_id} "
                    f"(Status code: {response.status_code})"
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch prediction data for {uniprot_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode prediction data for {uniprot_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching prediction data for {uniprot_id}: {e}")
            return None

    def _get_similar_proteins_count(self, uniprot_id: str) -> Optional[int]:
        """
        Fetch the number of similar proteins from AlphaFold clusters.

        Args:
            uniprot_id (str): The UniProt ID to get cluster data for.

        Returns:
            Optional[int]: The number of similar proteins if found, None otherwise.
        """
        logger.info(f"Querying for protein clusters count: {uniprot_id}")

        cluster_url = f"{ALPHAFOLD_CLUSTER_URL}/{uniprot_id}"
        params = {
            "cluster_flag": "AFDB50/MMseqs2",
            "records": 5,
            "start": 0,
            "sort_direction": "DESC",
            "sort_column": "averagePlddt",
        }

        try:
            response = requests.get(cluster_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()
            cluster_total = result.get("clusterTotal")

            if cluster_total is not None:
                logger.info(f"Found {cluster_total} similar proteins for {uniprot_id}")
                return cluster_total
            else:
                logger.warning(f"No cluster data found for {uniprot_id}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch cluster data for {uniprot_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode cluster data for {uniprot_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching cluster data for {uniprot_id}: {e}")
            return None

    def _parse_prediction_data(
        self, prediction_data: dict, uniprot_id: str, similar_proteins_count: Optional[int]
    ) -> AlphaFoldData:
        """
        Parse prediction data into AlphaFoldData object.

        Args:
            prediction_data (dict): Raw prediction data from AlphaFold API.
            uniprot_id (str): The UniProt ID.
            similar_proteins_count (Optional[int]): Count of similar proteins.

        Returns:
            AlphaFoldData: Parsed AlphaFold data.
        """
        try:
            aa_length = prediction_data.get("sequenceEnd")
            plddt = prediction_data.get("globalMetricValue")
            pdb_url = prediction_data.get("pdbUrl")

            # Check for Alpha Missense annotations
            missense_annotations = prediction_data.get("amAnnotationsUrl")
            has_alpha_missense = bool(
                missense_annotations
                and isinstance(missense_annotations, list)
                and len(missense_annotations) > 0
            )

            if has_alpha_missense:
                logger.info(f"Found Alpha Missense annotations for {uniprot_id}")
            else:
                logger.info(f"No Alpha Missense annotations found for {uniprot_id}")

            return AlphaFoldData(
                uniprot_id=uniprot_id,
                aa_length=aa_length,
                plddt=plddt,
                pdb_url=pdb_url,
                similar_proteins_count=similar_proteins_count,
                has_alpha_missense=has_alpha_missense,
                raw_data=prediction_data,
            )

        except Exception as e:
            logger.error(f"Error parsing prediction data for {uniprot_id}: {e}")
            return AlphaFoldData(
                uniprot_id=uniprot_id,
                error=f"Failed to parse prediction data: {str(e)}",
            )

    def validate_connection(self) -> bool:
        """
        Test the connection to AlphaFold API.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            # Test with a simple search query
            test_response = requests.get(
                ALPHAFOLD_SEARCH_URL,
                params={"q": "test", "type": "main", "start": 0, "rows": 1},
                timeout=self.timeout,
            )
            return test_response.status_code == 200
        except Exception as e:
            logger.warning(f"AlphaFold connection test failed: {e}")
            return False