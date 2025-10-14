"""
Departments resource class for Loket SDK.

This module provides methods for interacting with employer departments-related endpoints
in the Loket API, including retrieving, creating, updating, and deleting department information.
"""

from typing import Optional, Tuple, Dict, Any
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.departments import DepartmentGet, DepartmentCreate, DepartmentUpdate


class Departments:
    """
    Handles all departments-related operations for Loket SDK.

    This class provides methods to interact with employer departments endpoints,
    including retrieving, creating, updating, and deleting department information.
    """

    def __init__(self, loket_instance):
        """
        Initialize the Departments resource.

        Args:
            loket_instance: The Loket client instance
        """
        self.loket = loket_instance

    def get(self, employer_id: Optional[str] = None, department_id: Optional[str] = None, filter_query: Optional[str] = None, order_by: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get departments data. Can retrieve either a list of departments for an employer or a specific department by ID.

        Args:
            employer_id: The unique identifier of the employer (for getting all departments)
            department_id: The unique identifier of the department (for getting specific department)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated department data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all departments for an employer
            valid_df, invalid_df = loket.departments.get(employer_id="xxx-xxx")

            # Get specific department by ID
            valid_df, invalid_df = loket.departments.get(department_id="yyy-yyy")

            # Get departments with filter (code greater than 1)
            valid_df, invalid_df = loket.departments.get(employer_id="xxx-xxx", filter_query="code gt 1")
        """
        try:
            # Determine endpoint and parameters based on input
            if department_id:
                if not department_id.strip():
                    raise ValueError("Department ID cannot be empty")

                # Get specific department by ID
                endpoint = f"providers/employers/departments/{department_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Extract content from response (get_by_id returns content object)
                if "content" in response_data:
                    department_data = response_data["content"]
                else:
                    department_data = response_data

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([department_data])

            elif employer_id:
                # Get all departments for employer
                endpoint = f"providers/employers/{employer_id}/departments"
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
                raise ValueError("Either employer_id or department_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, DepartmentGet)

            return valid_data, invalid_data

        except Exception as e:
            if department_id:
                raise Exception(f"Failed to get department {department_id}: {e}")
            else:
                raise Exception(f"Failed to get departments for employer {employer_id}: {e}")

    def create(self, employer_id: str, data: Dict[str, Any]) -> Response:
        """
        Create a new department for an employer.

        Args:
            employer_id: The unique identifier of the employer
            data: Department data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the department data is invalid

        Example:
            # Create department with flat data structure
            response = loket.departments.create(
                employer_id="xxx-xxx",
                data={
                    "code": 2,
                    "description": "Verkoop Binnendienst",
                    "sub_department_of_key": "b14acd0d-75d7-4fc8-8b22-4a3924585cab",
                    "email_leave_request": "api@loket.nl"
                }
            )
        """
        if not employer_id or not employer_id.strip():
            raise ValueError("Employer ID cannot be empty")

        try:
            # Validate and convert flat data to nested structure
            department_data = DepartmentCreate(**data)
            request_body = department_data.model_dump(by_alias=True, exclude_none=True)
            # Make POST request to create department
            response = self.loket.session.post(
                url=f"{self.loket.base_url}/providers/employers/{employer_id}/departments",
                json=request_body,
                timeout=self.loket.timeout,
            )
            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to create department for employer {employer_id}: {e}")

    def update(self, department_id: str, **kwargs) -> Response:
        """
        Update an existing department.

        Args:
            department_id: The unique identifier of the department to update
            **kwargs: Department data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the department data is invalid

        Example:
            # Update department with flat data structure
            response = loket.departments.update(
                department_id="xxx-xxx",
                description="Verkoop Binnendienst Updated",
                sub_department_of_key="b14acd0d-75d7-4fc8-8b22-4a3924585cab",
                email_leave_request="updated@loket.nl"
            )
        """
        try:
            # Validate and convert flat data to nested structure
            department_data = DepartmentUpdate(**kwargs)
            request_body = department_data.model_dump(by_alias=True, exclude_none=True)
            # Make PUT request to update department
            response = self.loket.session.put(
                url=f"{self.loket.base_url}/providers/employers/departments/{department_id}",
                json=request_body,
                timeout=self.loket.timeout,
            )
            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to update department {department_id}: {e}")
