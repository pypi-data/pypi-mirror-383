"""
Year End Statements resource class for Loket SDK.

This module provides methods for interacting with year end statements endpoints
in the Loket API, including retrieving year end statements and downloading PDFs.
"""

from typing import Optional, Tuple
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions as BrynQFunctions
from .schemas.year_end_statements import YearEndStatementsGet


class YearEndStatements:
    """
    Handles all year end statements-related operations for Loket SDK.

    This class provides methods to interact with year end statements endpoints,
    including retrieving year end statements and downloading PDFs.
    """

    def __init__(self, loket_instance):
        """
        Initialize the YearEndStatements resource.

        Args:
            loket_instance: The Loket client instance
        """
        self.loket = loket_instance

    def get(
        self,
        employment_id: str,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get year end statements for a specific employment.

        Args:
            employment_id: The unique identifier of the employment
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated year end statements data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the employment ID is invalid

        Example:
            # Get all year end statements for a specific employment
            valid_df, invalid_df = loket.year_end_statements.get(employment_id="xxx-xxx")
        """
        if not employment_id or not employment_id.strip():
            raise ValueError("Employment ID cannot be empty")

        try:
            # Get year end statements for employment
            endpoint = f"providers/employers/employees/employments/{employment_id}/yearendstatements"
            response_data = self.loket.get(
                endpoint=endpoint,
                filter_query=filter_query,
                order_by=order_by,
                get_all_pages=True
            )

            # Convert to DataFrame for validation
            if not response_data:
                return pd.DataFrame(), pd.DataFrame()

            # Normalize nested JSON structure (list of items)
            df = pd.json_normalize(response_data)

            if df.empty:
                return pd.DataFrame(), pd.DataFrame()

            # Validate data using Pandera schema
            valid_data, invalid_data = BrynQFunctions.validate_data(df, YearEndStatementsGet)

            return valid_data, invalid_data

        except Exception as e:
            raise Exception(f"Failed to get year end statements for employment {employment_id}: {e}")

    def download(
        self,
        employment_id: str,
        year: int,
    ) -> Response:
        """
        Download year end statement PDF for a specific employment and year.

        Args:
            employment_id: The unique identifier of the employment
            year: The year to download year end statement for

        Returns:
            Response: Response object with PDF content

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the employment ID or year is invalid

        Example:
            # Download year end statement PDF for 2024
            response = loket.year_end_statements.download(employment_id="xxx-xxx", year=2024)
            with open("year_end_statement.pdf", "wb") as f:
                f.write(response.content)
        """
        if not employment_id or not employment_id.strip():
            raise ValueError("Employment ID cannot be empty")
        if not isinstance(year, int) or year < 1900 or year > 2100:
            raise ValueError("Year must be a valid integer between 1900 and 2100")

        try:
            # Download PDF for specific year
            response = self.loket.session.get(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/yearendstatements/{year}",
                timeout=self.loket.timeout,
            )
            response.raise_for_status()
            return response

        except Exception as e:
            raise Exception(f"Failed to download year end statement for employment {employment_id} and year {year}: {e}")
