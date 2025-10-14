from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from brynq_sdk_functions import Functions
from .schemas.providers import ProviderGet


class Providers:
    """
    Handles all provider-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize Providers manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance
        self.endpoint = "providers"
    def get(
        self,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a list of all providers accessible to the current user.

        Note: With the current functioning of Loket, the list will always contain 1 provider.
        This endpoint is typically not relevant for most external parties, as the GetEmployerByUser
        endpoint will be much more relevant as starting point.

        Args:
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated provider data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all providers
            valid_df, invalid_df = loket.providers.get()

            # Get providers with filter (name contains 'Tech')
            valid_df, invalid_df = loket.providers.get(filter_query="name lk 'Tech'")
        """
        # Get all pages automatically
        response_data = self.loket.get(
            endpoint=self.endpoint,
            filter_query=filter_query,
            order_by=order_by,
            get_all_pages=True
        )

        # Convert to DataFrame for validation
        if not response_data:
            # Return empty DataFrames if no data
            return pd.DataFrame(), pd.DataFrame()

        df = pd.DataFrame(response_data)

        # Validate data using Pandera schema
        valid_data, invalid_data = Functions.validate_data(df, ProviderGet)

        return valid_data, invalid_data
