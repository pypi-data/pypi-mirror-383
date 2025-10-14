"""
Functions resource class for Loket SDK.

This module provides methods for interacting with employer functions-related endpoints
in the Loket API, including retrieving, creating, and updating function information.
"""

from typing import Optional, Tuple, Dict, Any
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions as BrynQFunctions
from .schemas.functions import FunctionGet, FunctionCreate


class Functions:
    """
    Handles all functions-related operations for Loket SDK.

    This class provides methods to interact with employer functions endpoints,
    including retrieving, creating, and updating function information.
    """

    def __init__(self, loket_instance):
        """
        Initialize the Functions resource.

        Args:
            loket_instance: The Loket client instance
        """
        self.loket = loket_instance

    def get(self, employer_id: Optional[str] = None, function_id: Optional[str] = None, filter_query: Optional[str] = None, order_by: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get functions data. Can retrieve either a list of functions for an employer or a specific function by ID.

        Args:
            employer_id: The unique identifier of the employer (for getting all functions)
            function_id: The unique identifier of the function (for getting specific function)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated function data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all functions for an employer
            valid_df, invalid_df = loket.functions.get(employer_id="xxx-xxx")

            # Get specific function by ID
            valid_df, invalid_df = loket.functions.get(function_id="yyy-yyy")

            # Get functions with filter (group equals 'Var')
            valid_df, invalid_df = loket.functions.get(employer_id="xxx-xxx", filter_query="group eq 'Var'")
        """
        try:
            # Determine endpoint and parameters based on input
            if function_id:
                if not function_id.strip():
                    raise ValueError("Function ID cannot be empty")

                # Get specific function by ID
                endpoint = f"providers/employers/functions/{function_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Extract content from response (get_by_id returns content object)
                if "content" in response_data:
                    function_data = response_data["content"]
                else:
                    function_data = response_data

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([function_data])

            elif employer_id:
                # Get all functions for employer
                endpoint = f"providers/employers/{employer_id}/functions"
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

            else:
                raise ValueError("Either employer_id or function_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = BrynQFunctions.validate_data(df, FunctionGet)

            return valid_data, invalid_data

        except Exception as e:
            if function_id:
                raise Exception(f"Failed to get function {function_id}: {e}")
            else:
                raise Exception(f"Failed to get functions for employer {employer_id}: {e}")

    def create(self, employer_id: str, data: Dict[str, Any]) -> Response:
        """
        Create a new function for an employer.

        Args:
            employer_id: The unique identifier of the employer
            data: Function data fields

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the function data is invalid

        Example:
            # Create function
            response = loket.functions.create(
                employer_id="xxx-xxx",
                data={
                    "description": "Directeur",
                    "group": "Var"
                }
            )
        """
        if not employer_id or not employer_id.strip():
            raise ValueError("Employer ID cannot be empty")

        try:
            # Validate data
            function_data = FunctionCreate(**data)
            request_body = function_data.model_dump(by_alias=True, exclude_none=True)

            # Make POST request to create function
            response = self.loket.session.post(
                url=f"{self.loket.base_url}/providers/employers/{employer_id}/functions",
                json=request_body,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to create function for employer {employer_id}: {e}")

    def update(self, function_id: str, **kwargs) -> Response:
        """
        Update an existing function.

        Args:
            function_id: The unique identifier of the function to update
            **kwargs: Function data fields

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the function data is invalid

        Example:
            # Update function
            response = loket.functions.update(
                function_id="xxx-xxx",
                description="Directeur Updated",
                group="Var"
            )
        """
        try:
            # Validate data
            function_data = FunctionCreate(**kwargs)
            request_body = function_data.model_dump(by_alias=True, exclude_none=True)

            # Make PUT request to update function
            response = self.loket.session.put(
                url=f"{self.loket.base_url}/providers/employers/functions/{function_id}",
                json=request_body,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to update function {function_id}: {e}")
