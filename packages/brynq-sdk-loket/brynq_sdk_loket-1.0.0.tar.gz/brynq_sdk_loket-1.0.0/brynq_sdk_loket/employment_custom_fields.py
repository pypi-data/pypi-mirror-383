from typing import Dict, Any, Optional, Tuple
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.employment_custom_fields import EmploymentCustomFieldsGet, EmploymentCustomFieldsCreate, EmploymentCustomFieldsUpdate


class EmploymentCustomFields:
    """
    Handles all employment custom fields-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize EmploymentCustomFields manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance

    def get(
        self,
        employment_id: Optional[str] = None,
        employment_custom_field_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get employment custom fields data. Can retrieve either a list of employment custom fields for an employment or a specific employment custom field by ID.

        Args:
            employment_id: The unique identifier of the employment (for getting all employment custom fields)
            employment_custom_field_id: The unique identifier of the employment custom field (for getting specific employment custom field)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated employment custom fields data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all employment custom fields for an employment
            valid_df, invalid_df = loket.employments.custom_fields.get(employment_id="xxx-xxx")

            # Get specific employment custom field by ID
            valid_df, invalid_df = loket.employments.custom_fields.get(employment_custom_field_id="yyy-yyy")

            # Get employment custom fields with filter (value not null)
            valid_df, invalid_df = loket.employments.custom_fields.get(employment_id="xxx-xxx", filter_query="value ne null")
        """
        try:
            # Determine endpoint and parameters based on input
            if employment_custom_field_id:
                # Get specific employment custom field by ID
                endpoint = f"providers/employers/employees/employments/customfields/{employment_custom_field_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([response_data.get("content")])

            elif employment_id:
                # Get all employment custom fields for employment
                endpoint = f"providers/employers/employees/employments/{employment_id}/customfields"
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
                raise ValueError("Either employment_id or employment_custom_field_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, EmploymentCustomFieldsGet)

            return valid_data, invalid_data

        except Exception as e:
            if employment_custom_field_id:
                raise ValueError(f"Failed to get employment custom field {employment_custom_field_id}: {e}")
            else:
                raise ValueError(f"Failed to get employment custom fields for employment {employment_id}: {e}")

    def create(
        self,
        employment_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create a new custom field value for a specific employment.

        Args:
            employment_id: The unique identifier of the employment
            data: Dictionary containing employment custom field data

        Returns:
            Response: API response from the create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "custom_field": {"id": "025ce09b-bff2-4b05-bcf0-711a89da7c08"},
                "value": "41"
            }
            response = loket.employments.custom_fields.create(employment_id="xxx-xxx", data=data)
        """
        try:
            # Convert flat data to nested structure using alias mapping
            nested_data = self.loket.flat_dict_to_nested_dict(data, EmploymentCustomFieldsCreate)
            # Validate input data using Pydantic schema
            validated_data = EmploymentCustomFieldsCreate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate employment custom fields create data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/customfields",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update(
        self,
        employment_custom_field_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update an existing employment custom field value.

        Args:
            employment_custom_field_id: The unique identifier of the employment custom field
            data: Dictionary containing employment custom field data to update

        Returns:
            Response: API response from the update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "value": "42"
            }
            response = loket.employments.custom_fields.update(
                employment_custom_field_id="xxx-xxx",
                data=data
            )
        """
        try:
            # Validate input data using Pydantic schema
            validated_data = EmploymentCustomFieldsUpdate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate employment custom fields update data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/customfields/{employment_custom_field_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def delete(
        self,
        employment_custom_field_id: str,
    ) -> Response:
        """
        Delete an existing employment custom field.

        Args:
            employment_custom_field_id: The unique identifier of the employment custom field

        Returns:
            Response: API response from the delete request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the request fails

        Example:
            response = loket.employments.custom_fields.delete(employment_custom_field_id="xxx-xxx")
        """
        try:
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/customfields/{employment_custom_field_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to delete employment custom field {employment_custom_field_id}: {e}")
