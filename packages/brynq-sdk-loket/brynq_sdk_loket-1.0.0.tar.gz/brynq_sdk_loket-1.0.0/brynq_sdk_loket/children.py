"""
Children resource class for Loket SDK.

This module provides methods for interacting with employee children-related endpoints
in the Loket API, including retrieving, creating, updating, and deleting child information.
"""

from typing import Optional, Tuple, Dict, Any
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.children import ChildGet, ChildCreate


class Children:
    """
    Handles all children-related operations for Loket SDK.

    This class provides methods to interact with employee children endpoints,
    including retrieving, creating, updating, and deleting child information.
    """

    def __init__(self, loket_instance):
        """
        Initialize the Children resource.

        Args:
            loket_instance: The Loket client instance
        """
        self.loket = loket_instance

    def get(self, employee_id: Optional[str] = None, child_id: Optional[str] = None, filter_query: Optional[str] = None, order_by: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get children data. Can retrieve either a list of children for an employee or a specific child by ID.

        Args:
            employee_id: The unique identifier of the employee (for getting all children)
            child_id: The unique identifier of the child (for getting specific child)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated child data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all children for an employee
            valid_df, invalid_df = loket.children.get(employee_id="xxx-xxx")

            # Get specific child by ID
            valid_df, invalid_df = loket.children.get(child_id="yyy-yyy")

            # Get children with filter (gender equals 'female')
            valid_df, invalid_df = loket.children.get(employee_id="xxx-xxx", filter_query="gender.value eq 'female'")
        """
        try:
            # Determine endpoint and parameters based on input
            if child_id:
                if not child_id.strip():
                    raise ValueError("Child ID cannot be empty")

                # Get specific child by ID
                endpoint = f"providers/employers/employees/children/{child_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Extract content from response (get_by_id returns content object)
                if "content" in response_data:
                    child_data = response_data["content"]
                else:
                    child_data = response_data

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([child_data])

            elif employee_id:
                # Get all children for employee
                endpoint = f"providers/employers/employees/{employee_id}/children"
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
                raise ValueError("Either employee_id or child_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, ChildGet)

            return valid_data, invalid_data

        except Exception as e:
            if child_id:
                raise Exception(f"Failed to get child {child_id}: {e}")
            else:
                raise Exception(f"Failed to get children for employee {employee_id}: {e}")

    def create(self, employee_id: str, data: Dict[str, Any]) -> Response:
        """
        Create a new child for an employee.

        Args:
            employee_id: The unique identifier of the employee
            data: Child data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the child data is invalid

        Example:
            # Create child with flat data structure
            response = loket.children.create(
                employee_id="xxx-xxx",
                data={
                    "first_name": "Susan",
                    "last_name": "Bergen",
                    "prefix": "van",
                    "initials": "S.L.",
                    "date_of_birth": "1995-05-21",
                    "date_of_death": "2019-08-24",
                    "gender_key": 2,
                    "residence_status_key": 2
                }
            )
        """
        if not employee_id or not employee_id.strip():
            raise ValueError("Employee ID cannot be empty")

        try:
            # Validate and convert flat data to nested structure
            child_data = ChildCreate(**data)
            request_body = child_data.model_dump(by_alias=True, exclude_none=True)

            # Make POST request to create child
            response = self.loket.session.post(
                url=f"{self.loket.base_url}/providers/employers/employees/{employee_id}/children",
                json=request_body,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to create child for employee {employee_id}: {e}")

    def update(self, child_id: str, **kwargs) -> Response:
        """
        Update an existing child.

        Args:
            child_id: The unique identifier of the child to update
            **kwargs: Child data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the child data is invalid

        Example:
            # Update child with flat data structure
            response = loket.children.update(
                child_id="xxx-xxx",
                first_name="Susan Updated",
                last_name="Bergen",
                prefix="van",
                initials="S.L.",
                date_of_birth="1995-05-21",
                date_of_death="2019-08-24",
                gender_key=2,
                residence_status_key=2
            )
        """
        try:
            # Validate and convert flat data to nested structure
            child_data = ChildCreate(**kwargs)
            request_body = child_data.model_dump(by_alias=True, exclude_none=True)

            # Make PUT request to update child
            response = self.loket.session.put(
                url=f"{self.loket.base_url}/providers/employers/employees/children/{child_id}",
                json=request_body,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to update child {child_id}: {e}")

    def delete(self, child_id: str) -> Response:
        """
        Delete an existing child.

        Args:
            child_id: The unique identifier of the child to delete

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the child_id is invalid

        Example:
            # Delete a child
            response = loket.children.delete(child_id="xxx-xxx")
        """
        try:
            if not child_id or not child_id.strip():
                raise ValueError("Child ID cannot be empty")

            # Make DELETE request to delete child
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/children/{child_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to delete child {child_id}: {e}")
