from typing import Dict, Any, Optional, Tuple
import pandas as pd

from brynq_sdk_functions import Functions
from .schemas.administrations import AdministrationGet


class Administrations:
    """
    Handles all administration-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize Administrations manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance

    def get_by_employer_id(
        self,
        employer_id: str,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a list of all administrations for a specific employer.

        Args:
            employer_id: The unique identifier of the employer
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated administration data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all administrations for an employer
            valid_df, invalid_df = loket.administrations.get_by_employer_id(employer_id="xxx-xxx")

            # Get administrations with filter (active only)
            valid_df, invalid_df = loket.administrations.get_by_employer_id(employer_id="xxx-xxx", filter_query="isActive eq true")
        """
        try:
            # Get all pages automatically
            endpoint = f"providers/employers/{employer_id}/administrations"
            response_data = self.loket.get(
                endpoint=endpoint,
                filter_query=filter_query,
                order_by=order_by,
                get_all_pages=True
            )

            # Convert to DataFrame for validation
            if not response_data:
                # Return empty DataFrames if no data
                return pd.DataFrame(), pd.DataFrame()

            # Normalize nested JSON structure
            df = pd.json_normalize(response_data)

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, AdministrationGet)

            return valid_data, invalid_data

        except Exception as e:
            raise Exception(f"Failed to get administrations for employer {employer_id}: {e}")

    def get(
        self,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a list of all administrations accessible to the current user.

        Args:
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated administration data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all administrations
            valid_df, invalid_df = loket.administrations.get()

            # Get administrations with filter (active only)
            valid_df, invalid_df = loket.administrations.get(filter_query="isActive eq true")
        """
        try:
            # Get all pages automatically
            endpoint = "providers/employers/administrations"
            response_data = self.loket.get(
                endpoint=endpoint,
                filter_query=filter_query,
                order_by=order_by,
                get_all_pages=True
            )

            # Convert to DataFrame for validation
            if not response_data:
                # Return empty DataFrames if no data
                return pd.DataFrame(), pd.DataFrame()

            # Normalize nested JSON structure
            df = pd.json_normalize(response_data)

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, AdministrationGet)

            return valid_data, invalid_data

        except Exception as e:
            raise Exception(f"Failed to get all administrations: {e}")
