from typing import Dict, Any, Optional, Tuple
import pandas as pd
from requests import Response
from brynq_sdk_functions import Functions
from .schemas.employee_custom_fields import EmployeeCustomFieldsGet, EmployeeCustomFieldsCreate, EmployeeCustomFieldsUpdate


class EmployeeCustomFields:
    def __init__(self, loket_instance):
        self.loket = loket_instance

    def get(
        self,
        employee_id: Optional[str] = None,
        employee_custom_field_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get employee custom fields data. Can retrieve either a list of employee custom fields for an employee or a specific employee custom field by ID.

        Args:
            employee_id: The unique identifier of the employee (for getting all employee custom fields)
            employee_custom_field_id: The unique identifier of the employee custom field (for getting specific employee custom field)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated employee custom fields data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all employee custom fields for an employee
            valid_df, invalid_df = loket.employee_custom_fields.get(employee_id="xxx-xxx")

            # Get specific employee custom field by ID
            valid_df, invalid_df = loket.employee_custom_fields.get(employee_custom_field_id="yyy-yyy")

            # Get employee custom fields with filter (value not null)
            valid_df, invalid_df = loket.employee_custom_fields.get(employee_id="xxx-xxx", filter_query="value ne null")
        """
        try:
            # Determine endpoint and parameters based on input
            if employee_custom_field_id:
                # Get specific employee custom field by ID
                endpoint = f"providers/employers/employees/customfields/{employee_custom_field_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([response_data.get("content")])

            elif employee_id:
                # Get all employee custom fields for employee
                endpoint = f"providers/employers/employees/{employee_id}/customfields"
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
                raise ValueError("Either employee_id or employee_custom_field_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, EmployeeCustomFieldsGet)

            return valid_data, invalid_data

        except Exception as e:
            if employee_custom_field_id:
                raise ValueError(f"Failed to get employee custom field {employee_custom_field_id}: {e}")
            else:
                raise ValueError(f"Failed to get employee custom fields for employee {employee_id}: {e}")

    def create(
        self,
        employee_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create employee custom field for a specific employee.
        """
        try:
            nested_data = self.loket.flat_dict_to_nested_dict(data, EmployeeCustomFieldsCreate)
            validated_data = EmployeeCustomFieldsCreate(**nested_data)

            response = self.loket.session.post(
                url=f"{self.loket.base_url}/providers/employers/employees/{employee_id}/customfields",
                json=validated_data.model_dump(by_alias=True, mode="json", exclude_none=True),
                timeout=self.loket.timeout,
            )
            response.raise_for_status()
            return response
        except Exception as exc:
            raise ValueError(f"Failed to validate employee custom field create data: {exc}")

    def update(
        self,
        employee_custom_field_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update employee custom field.
        """
        try:
            nested_data = self.loket.flat_dict_to_nested_dict(data, EmployeeCustomFieldsUpdate)
            validated_data = EmployeeCustomFieldsUpdate(**nested_data)

            response = self.loket.session.put(
                url=f"{self.loket.base_url}/providers/employers/employees/customfields/{employee_custom_field_id}",
                json=validated_data.model_dump(by_alias=True, mode="json", exclude_none=True),
                timeout=self.loket.timeout,
            )
            response.raise_for_status()
            return response
        except Exception as exc:
            raise ValueError(f"Failed to validate employee custom field update data: {exc}")

    def delete(
        self,
        employee_custom_field_id: str,
    ) -> Response:
        """
        Delete employee custom field.
        """
        try:
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/customfields/{employee_custom_field_id}",
                timeout=self.loket.timeout,
            )
            response.raise_for_status()
            return response
        except Exception as e:
            raise ValueError(f"Failed to delete employee custom field {employee_custom_field_id}: {e}")
