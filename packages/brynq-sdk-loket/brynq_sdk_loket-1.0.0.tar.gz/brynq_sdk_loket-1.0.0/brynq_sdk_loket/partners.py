"""
Partners resource class for Loket SDK.

This module provides methods for interacting with employee partners-related endpoints
in the Loket API, including retrieving, creating, updating, and deleting partner information.
"""

from typing import Optional, Tuple, Dict, Any
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.partners import PartnerGet, PartnerCreate


class Partners:
    """
    Handles all partners-related operations for Loket SDK.

    This class provides methods to interact with employee partners endpoints,
    including retrieving, creating, updating, and deleting partner information.
    """

    def __init__(self, loket_instance):
        """
        Initialize the Partners resource.

        Args:
            loket_instance: The Loket client instance
        """
        self.loket = loket_instance

    def get(self, employee_id: Optional[str] = None, partner_id: Optional[str] = None, filter_query: Optional[str] = None, order_by: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get partners data. Can retrieve either a list of partners for an employee or a specific partner by ID.

        Args:
            employee_id: The unique identifier of the employee (for getting all partners)
            partner_id: The unique identifier of the partner (for getting specific partner)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated partner data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all partners for an employee
            valid_df, invalid_df = loket.partners.get(employee_id="xxx-xxx")

            # Get specific partner by ID
            valid_df, invalid_df = loket.partners.get(partner_id="yyy-yyy")

            # Get partners with filter (gender equals 'female')
            valid_df, invalid_df = loket.partners.get(employee_id="xxx-xxx", filter_query="gender.value eq 'female'")
        """
        try:
            # Determine endpoint and parameters based on input
            if partner_id:
                if not partner_id.strip():
                    raise ValueError("Partner ID cannot be empty")

                # Get specific partner by ID
                endpoint = f"providers/employers/employees/partners/{partner_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Extract content from response (get_by_id returns content object)
                if "content" in response_data:
                    partner_data = response_data["content"]
                else:
                    partner_data = response_data

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([partner_data])

            elif employee_id:
                # Get all partners for employee
                endpoint = f"providers/employers/employees/{employee_id}/partners"
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
                raise ValueError("Either employee_id or partner_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, PartnerGet)

            return valid_data, invalid_data

        except Exception as e:
            if partner_id:
                raise Exception(f"Failed to get partner {partner_id}: {e}")
            else:
                raise Exception(f"Failed to get partners for employee {employee_id}: {e}")

    def create(self, employee_id: str, data: Dict[str, Any]) -> Response:
        """
        Create a new partner for an employee.

        Args:
            employee_id: The unique identifier of the employee
            data: Partner data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the partner data is invalid

        Example:
            # Create partner with flat data structure
            response = loket.partners.create(
                employee_id="xxx-xxx",
                data={
                    "start_date": "1995-05-21",
                    "end_date": "1995-05-21",
                    "first_name": "Susan",
                    "last_name": "Bergen",
                    "prefix": "van",
                    "initials": "S.L.",
                    "date_of_birth": "1995-05-21",
                    "place_of_birth": "Amsterdam",
                    "date_of_death": "2019-08-24",
                    "how_to_format_last_name_key": 2,
                    "title_key": 2,
                    "gender_key": 2,
                    "wao_classification_key": 2
                }
            )
        """
        if not employee_id or not employee_id.strip():
            raise ValueError("Employee ID cannot be empty")

        try:
            # Validate and convert flat data to nested structure
            partner_data = PartnerCreate(**data)
            request_body = partner_data.model_dump(by_alias=True, exclude_none=True)
            # Make POST request to create partner
            response = self.loket.session.post(
                url=f"{self.loket.base_url}/providers/employers/employees/{employee_id}/partners",
                json=request_body,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to create partner for employee {employee_id}: {e}")

    def update(self, partner_id: str, **kwargs) -> Response:
        """
        Update an existing partner.

        Args:
            partner_id: The unique identifier of the partner to update
            **kwargs: Partner data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the partner data is invalid

        Example:
            # Update partner with flat data structure
            response = loket.partners.update(
                partner_id="xxx-xxx",
                start_date="1995-05-21",
                end_date="1995-05-21",
                first_name="Susan Updated",
                last_name="Bergen",
                prefix="van",
                initials="S.L.",
                date_of_birth="1995-05-21",
                place_of_birth="Amsterdam",
                date_of_death="2019-08-24",
                how_to_format_last_name_key=2,
                title_key=2,
                gender_key=2,
                wao_classification_key=2
            )
        """
        try:
            # Validate and convert flat data to nested structure
            partner_data = PartnerCreate(**kwargs)
            request_body = partner_data.model_dump(by_alias=True, exclude_none=True)

            # Make PUT request to update partner
            response = self.loket.session.put(
                url=f"{self.loket.base_url}/providers/employers/employees/partners/{partner_id}",
                json=request_body,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to update partner {partner_id}: {e}")

    def delete(self, partner_id: str) -> Response:
        """
        Delete an existing partner.

        Args:
            partner_id: The unique identifier of the partner to delete

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the partner_id is invalid

        Example:
            # Delete a partner
            response = loket.partners.delete(partner_id="xxx-xxx")
        """
        try:
            if not partner_id or not partner_id.strip():
                raise ValueError("Partner ID cannot be empty")

            # Make DELETE request to delete partner
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/partners/{partner_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to delete partner {partner_id}: {e}")
