"""Service for interacting with NCBI API."""

import logging
from typing import Optional

import requests

from ..core.models import NCBIData
from ..shared.constants import NCBI_BASE_URL, DEFAULT_TIMEOUT_SECONDS
from ..shared.exceptions import NCBIError
from ..shared.utils import extract_locus_tag, extract_definition

logger = logging.getLogger(__name__)


class NCBIService:
    """Service for fetching protein data from NCBI."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        """
        Initialize the NCBI service.

        Args:
            timeout (int): Request timeout in seconds.
        """
        self.timeout = timeout

    def get_protein_data(self, protein_id: str) -> NCBIData:
        """
        Fetch locus tag and protein description from NCBI.

        Args:
            protein_id (str): The protein ID to query.

        Returns:
            NCBIData: Object containing the fetched data or error information.

        Raises:
            NCBIError: If the API request fails critically.
        """
        logger.info(f"Querying NCBI for protein ID: {protein_id}")

        params = {
            "db": "protein",
            "id": protein_id,
            "rettype": "gb",
            "retmode": "text",
        }

        try:
            response = requests.get(
                NCBI_BASE_URL, params=params, timeout=self.timeout
            )
            response.raise_for_status()

            content = response.text
            locus_tag = extract_locus_tag(content) or "Not Found"
            definition = extract_definition(content) or "Not Found"

            logger.info(
                f"Successfully fetched NCBI data for {protein_id}: "
                f"locus_tag={locus_tag}, definition={definition[:50]}..."
            )

            return NCBIData(locus_tag=locus_tag, description=definition)

        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout while fetching data from NCBI for {protein_id}"
            logger.warning(f"{error_msg}: {e}")
            return NCBIData(
                locus_tag="Error", description="Error", error=error_msg
            )

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch data from NCBI for {protein_id}"
            logger.error(f"{error_msg}: {e}")
            return NCBIData(
                locus_tag="Error", description="Error", error=error_msg
            )

        except Exception as e:
            error_msg = f"Unexpected error while processing NCBI data for {protein_id}"
            logger.error(f"{error_msg}: {e}")
            raise NCBIError(error_msg) from e

    def validate_connection(self) -> bool:
        """
        Test the connection to NCBI API.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            # Test with a simple query
            test_response = requests.get(
                NCBI_BASE_URL,
                params={"db": "protein", "id": "test", "rettype": "gb", "retmode": "text"},
                timeout=self.timeout,
            )
            # Even if the specific ID doesn't exist, we should get a response from the server
            return test_response.status_code in [200, 400]  # 400 is expected for invalid ID
        except Exception as e:
            logger.warning(f"NCBI connection test failed: {e}")
            return False