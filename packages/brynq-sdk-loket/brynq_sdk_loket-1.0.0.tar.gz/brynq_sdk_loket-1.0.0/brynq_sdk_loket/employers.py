from typing import Dict, Any, Optional, Tuple
import pandas as pd

from brynq_sdk_functions import Functions
from .schemas.employers import EmployerGet, EmployerMinimizedGet, EmployerUpdate, EmployerCreate
from .custom_fields import CustomFields


class Employers:
    """
    Handles all employer-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize Employers manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance
        self.endpoint = "providers/employers"

        # Initialize sub-resources
        self.custom_fields = CustomFields(loket_instance)

    def get(
        self,
        employer_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get employers data. Can retrieve either a list of all employers or a specific employer by ID.

        Args:
            employer_id: The unique identifier of the employer (for getting specific employer)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated employer data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all employers
            valid_df, invalid_df = loket.employers.get()

            # Get specific employer by ID
            valid_df, invalid_df = loket.employers.get(employer_id="xxx-xxx")

            # Get employers with filter (company name contains 'Tech')
            valid_df, invalid_df = loket.employers.get(filter_query="companyName lk 'Tech'")
        """
        try:
            # Determine endpoint and parameters based on input
            if employer_id:
                # Get specific employer by ID
                endpoint = f"{self.endpoint}/{employer_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data or "content" not in response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Extract content from response wrapper
                employer_data = response_data["content"]

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([employer_data])

            else:
                # Get all employers
                response_data = self.loket.get(
                    endpoint=self.endpoint,
                    filter_query=filter_query,
                    order_by=order_by,
                    get_all_pages=True
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Normalize nested JSON structure (list of items)
                df = pd.json_normalize(response_data)

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, EmployerGet)

            return valid_data, invalid_data

        except Exception as e:
            if employer_id:
                raise Exception(f"Failed to get employer {employer_id}: {e}")
            else:
                raise Exception(f"Failed to get employers: {e}")

    def get_minimized(
        self,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a minimized list of all employers accessible to the current user.
        This endpoint returns a simplified version of employer data.

        Args:
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated employer data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid
        """
        try:
            # Get all pages automatically
            response_data = self.loket.get(
                endpoint=f"{self.endpoint}/minimized",
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

            # Validate data using Pandera schema (minimized schema)
            valid_data, invalid_data = Functions.validate_data(df, EmployerMinimizedGet)

            return valid_data, invalid_data

        except Exception as e:
            raise Exception(f"Failed to get minimized employers: {e}")

    def get_by_provider_id(
        self,
        provider_id: str,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a minimized list of employers for a specific provider.
        This endpoint returns a simplified version of employer data for the given provider.

        Args:
            provider_id: The unique identifier of the provider
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated employer data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid
        """
        try:
            # Get all pages automatically
            response_data = self.loket.get(
                endpoint=f"providers/{provider_id}/employers/minimized",
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

            # Validate data using Pandera schema (minimized schema)
            valid_data, invalid_data = Functions.validate_data(df, EmployerMinimizedGet)

            return valid_data, invalid_data

        except Exception as e:
            raise Exception(f"Failed to get employers for provider {provider_id}: {e}")



    def update(
        self,
        employer_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an employer by its ID.
        This endpoint updates employer information for the given employer ID.

        Args:
            employer_id: The unique identifier of the employer
            data: Flat dictionary containing employer data to update

        Returns:
            Dict[str, Any]: Updated employer data from the API response

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid
        """

        try:
            # Validate and transform flat dict to nested via schema validator
            validated_data = EmployerUpdate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode='json', exclude_none=True)
        except Exception as e:
            raise Exception(f"Failed to update employer data: {e}")

        # Make PUT request to update employer
        response = self.loket.session.put(
            url=f"{self.loket.base_url}/{self.endpoint}/{employer_id}",
            json=request_body,
            timeout=self.loket.timeout
        )
        response.raise_for_status()

        return response.json()

    def create(
        self,
        provider_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new employer for a specific provider.
        This endpoint creates a new employer with the provided information.

        Args:
            provider_id: The unique identifier of the provider
            data: Flat dictionary containing employer data to create

        Returns:
            Dict[str, Any]: Created employer data from the API response

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid
        """

        try:
            # Validate and transform flat dict to nested via schema validator
            validated_data = EmployerCreate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode='json', exclude_none=True)
        except Exception as e:
            raise Exception(f"Failed to create employer data: {e}")

        # Make POST request to create employer
        endpoint = f"providers/{provider_id}/employers"
        response = self.loket.session.post(
            url=f"{self.loket.base_url}/{endpoint}",
            json=request_body,
            timeout=self.loket.timeout
        )
        response.raise_for_status()

        return response.json()
