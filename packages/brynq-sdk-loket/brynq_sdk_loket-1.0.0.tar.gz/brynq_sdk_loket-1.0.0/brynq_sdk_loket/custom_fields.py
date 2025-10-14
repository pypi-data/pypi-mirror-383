from typing import Dict, Any, Optional, Tuple
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.custom_fields import CustomFieldsGet, CustomFieldsCreate, CustomFieldsUpdate


class CustomFields:
    """
    Handles all custom fields-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize CustomFields manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance

    def get(
        self,
        employer_id: Optional[str] = None,
        custom_field_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get custom fields data. Can retrieve either a list of custom fields for an employer or a specific custom field by ID.

        Args:
            employer_id: The unique identifier of the employer (for getting all custom fields)
            custom_field_id: The unique identifier of the custom field (for getting specific custom field)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated custom fields data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all custom fields for an employer
            valid_df, invalid_df = loket.custom_fields.get(employer_id="xxx-xxx")

            # Get specific custom field by ID
            valid_df, invalid_df = loket.custom_fields.get(custom_field_id="yyy-yyy")

            # Get custom fields with filter (active fields only)
            valid_df, invalid_df = loket.custom_fields.get(employer_id="xxx-xxx", filter_query="isActive eq true")
        """
        try:
            # Determine endpoint and parameters based on input
            if custom_field_id:
                # Get specific custom field by ID
                endpoint = f"providers/employers/customfields/{custom_field_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([response_data.get("content")])

            elif employer_id:
                # Get all custom fields for employer
                endpoint = f"providers/employers/{employer_id}/customfields"
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
                raise ValueError("Either employer_id or custom_field_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, CustomFieldsGet)

            return valid_data, invalid_data

        except Exception as e:
            if custom_field_id:
                raise ValueError(f"Failed to get custom field {custom_field_id}: {e}")
            else:
                raise ValueError(f"Failed to get custom fields for employer {employer_id}: {e}")

    def create(
        self,
        employer_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create a new custom field for a specific employer.

        Args:
            employer_id: The unique identifier of the employer
            data: Dictionary containing custom field data

        Returns:
            Response: API response from the create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "description": "Shoe size"
            }
            response = loket.custom_fields.create(employer_id="xxx-xxx", data=data)
        """
        try:
            # Validate input data using Pydantic schema
            validated_data = CustomFieldsCreate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate custom fields create data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/{employer_id}/customfields",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update(
        self,
        custom_field_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update an existing custom field.

        Args:
            custom_field_id: The unique identifier of the custom field
            data: Dictionary containing custom field data to update

        Returns:
            Response: API response from the update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "description": "Shoe size"
            }
            response = loket.custom_fields.update(
                custom_field_id="xxx-xxx",
                data=data
            )
        """
        try:
            # Validate input data using Pydantic schema
            validated_data = CustomFieldsUpdate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate custom fields update data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/customfields/{custom_field_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def delete(
        self,
        custom_field_id: str,
    ) -> Response:
        """
        Delete an existing custom field.

        Args:
            custom_field_id: The unique identifier of the custom field

        Returns:
            Response: API response from the delete request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the request fails

        Example:
            response = loket.custom_fields.delete(custom_field_id="xxx-xxx")
        """
        try:
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/customfields/{custom_field_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to delete custom field {custom_field_id}: {e}")
