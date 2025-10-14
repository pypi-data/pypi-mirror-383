from typing import Dict, Any, Optional, Tuple
import pandas as pd

from brynq_sdk_functions import Functions
from .schemas.employments import EmploymentGet, EmploymentUpdate, EmploymentTerminate
from .employment_custom_fields import EmploymentCustomFields
from requests import Response


class Employments:
    """
    Handles all employment-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize Employments manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance

        # Initialize sub-resources
        self.custom_fields = EmploymentCustomFields(loket_instance)

    def get(
        self,
        employer_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        employment_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get employments data. Can retrieve either a list of employments for an employer/employee or a specific employment by ID.

        Args:
            employer_id: The unique identifier of the employer (for getting all employments for employer)
            employee_id: The unique identifier of the employee (for getting all employments for employee)
            employment_id: The unique identifier of the employment (for getting specific employment)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated employment data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all employments for an employer
            valid_df, invalid_df = loket.employments.get(employer_id="xxx-xxx")

            # Get all employments for an employee
            valid_df, invalid_df = loket.employments.get(employee_id="yyy-yyy")

            # Get specific employment by ID
            valid_df, invalid_df = loket.employments.get(employment_id="zzz-zzz")

            # Get employments with filter (no end date)
            valid_df, invalid_df = loket.employments.get(employer_id="xxx-xxx", filter_query="endDate eq null")
        """
        try:
            # Determine endpoint and parameters based on input
            if employment_id:
                # Get specific employment by ID
                endpoint = f"providers/employers/employees/employments/{employment_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                records: list[Dict[str, Any]]
                if isinstance(response_data, list):
                    records = response_data
                elif isinstance(response_data, dict):
                    content = response_data.get("content")
                    if isinstance(content, list):
                        records = content
                    elif content:
                        records = [content]
                    else:
                        records = [response_data]
                else:
                    records = [response_data]

                if not records:
                    return pd.DataFrame(), pd.DataFrame()

                df = pd.json_normalize(records)

            elif employer_id:
                # Get all employments for employer
                endpoint = f"providers/employers/{employer_id}/employees/employments"
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

            elif employee_id:
                # Get all employments for employee
                endpoint = f"providers/employers/employees/{employee_id}/employments"
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
                raise ValueError("Either employer_id, employee_id, or employment_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, EmploymentGet)

            return valid_data, invalid_data

        except Exception as e:
            if employment_id:
                raise Exception(f"Failed to get employment {employment_id}: {e}")
            elif employer_id:
                raise Exception(f"Failed to get employments for employer {employer_id}: {e}")
            else:
                raise Exception(f"Failed to get employments for employee {employee_id}: {e}")


    def update(
        self,
        employment_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update an employment by its ID using flat payload input.

        Args:
            employment_id: The unique identifier of the employment
            data: Flat dictionary containing employment fields to update

        Returns:
            Dict[str, Any]: Updated employment data from the API response

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid
        """
        try:
            nested_data = self.loket.flat_dict_to_nested_dict(data, EmploymentUpdate)
            validated_data = EmploymentUpdate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)
        except Exception as exc:
            raise Exception(f"Failed to update employment data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def delete(
        self,
        employment_id: str,
    ) -> Response:
        """
        Delete an employment by its ID.

        Args:
            employment_id: The unique identifier of the employment to remove

        Returns:
            Dict[str, Any]: API response payload (empty dict when no content is returned)

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        try:
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}",
                timeout=self.loket.timeout,
            )
            response.raise_for_status()
        except Exception as exc:
            raise Exception(f"Failed to delete employment {employment_id}: {exc}")

        return response

    def terminate(
        self,
        employment_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Terminate an employment by its ID.

        Args:
            employment_id: The unique identifier of the employment to terminate
            data: Dictionary containing termination data with the following fields:
                - end_date (str): The date on which the employment ends (mandatory)
                - end_of_employment_reason (dict, optional): Legacy reason for termination
                - end_of_employment_due_to_illness (bool, optional): Whether termination is due to illness
                - create_mdv_entry (bool, optional): Whether to generate MDV entry automatically
                - end_of_employment_reason_tax_authorities (dict, optional): Tax authority reason

        Returns:
            Response: API response from the termination request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            termination_data = {
                "end_date": "2024-12-31",
                "end_of_employment_due_to_illness": False,
                "create_mdv_entry": False,
                "end_of_employment_reason_tax_authorities": {
                    "key": 8,
                    "value": "Other"
                }
            }
            response = employments.terminate("emp123", termination_data)
        """
        try:
            # Convert flat data to nested structure using alias mapping
            nested_data = self.loket.flat_dict_to_nested_dict(data, EmploymentTerminate)

            # Validate input data using Pydantic schema
            validated_data = EmploymentTerminate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise Exception(f"Failed to validate termination data: {exc}")

        response = self.loket.session.patch(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/terminate",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def reinstate(
        self,
        employment_id: str,
    ) -> Response:
        """
        Reinstate (undo termination) an employment by its ID.
        This endpoint reverses the termination of an employment.

        Args:
            employment_id: The unique identifier of the employment to reinstate

        Returns:
            Response: API response from the reinstate request

        Raises:
            requests.exceptions.RequestException: If the API request fails

        Example:
            response = employments.reinstate("emp123")
        """
        try:
            # Make PATCH request to reinstate employment
            # No request body needed, but Accept header is important for resource version
            headers = {
                "Accept": "application/json;version=2018-01-01"
            }

            response = self.loket.session.patch(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/reinstate",
                headers=headers,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as exc:
            raise Exception(f"Failed to reinstate employment {employment_id}: {exc}")
