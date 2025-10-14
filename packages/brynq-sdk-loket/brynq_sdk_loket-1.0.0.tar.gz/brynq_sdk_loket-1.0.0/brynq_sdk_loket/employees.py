from typing import Dict, Any, Optional, Tuple
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.employees import EmployeeGet, EmployeeUpdate, EmployeeBsnUpdate, EmployeeCreate
from .absences import Absences
from .employee_custom_fields import EmployeeCustomFields


class Employees:
    """
    Handles all employee-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize Employees manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance

        # Initialize sub-resources
        self.absences = Absences(loket_instance)
        self.custom_fields = EmployeeCustomFields(loket_instance)

    def get(
        self,
        employer_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get employees data. Can retrieve either a list of employees for an employer or a specific employee by ID.

        Args:
            employer_id: The unique identifier of the employer (for getting all employees)
            employee_id: The unique identifier of the employee (for getting specific employee)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated employee data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all employees for an employer
            valid_df, invalid_df = loket.employees.get(employer_id="xxx-xxx")

            # Get specific employee by ID
            valid_df, invalid_df = loket.employees.get(employee_id="yyy-yyy")

            # Get employees with filter (employee numbers between 1 and 100)
            valid_df, invalid_df = loket.employees.get(employer_id="xxx-xxx", filter_query="employeeNumber ge 1 and employeeNumber le 100")
        """
        try:
            # Determine endpoint and parameters based on input
            if employee_id:
                # Get specific employee by ID
                endpoint = f"providers/employers/employees/{employee_id}"
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
                # Get all employees for employer
                endpoint = f"providers/employers/{employer_id}/employees"
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
                raise ValueError("Either employer_id or employee_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, EmployeeGet)

            return valid_data, invalid_data

        except Exception as e:
            if employee_id:
                raise Exception(f"Failed to get employee {employee_id}: {e}")
            else:
                raise Exception(f"Failed to get employees for employer {employer_id}: {e}")

    def update(
        self,
        employee_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update an employee by its ID using flat payload input.

        Args:
            employee_id: The unique identifier of the employee
            data: Flat dictionary containing employee fields to update

        Returns:
            Response: API response from the update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid
        """
        try:
            # Validate input data using Pydantic schema
            # The flat_to_nested validator on the schema will handle flat-to-nested conversion
            validated_data = EmployeeUpdate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise Exception(f"Failed to validate employee update data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/employees/{employee_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update_bsn_number(
        self,
        employee_id: str,
        citizen_service_number: Optional[str] = None,
    ) -> Response:
        """
        Update the BSN (citizen service number) of an employee.

        This endpoint updates the social security number of the employee used in
        communication with the Dutch tax authorities. The number has to be a
        valid Dutch citizen service number (BSN) with exactly 9 digits.

        Args:
            employee_id: The unique identifier of the employee
            citizen_service_number: The 9-digit Dutch citizen service number (BSN).
                                  Can be None to clear the BSN.

        Returns:
            Response: API response from the BSN update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the BSN format is invalid

        Example:
            # Update BSN
            response = loket.employees.update_bsn_number("emp123", "123456789")

            # Clear BSN
            response = loket.employees.update_bsn_number("emp123", None)
        """
        try:
            # Validate input data using Pydantic schema
            validated_data = EmployeeBsnUpdate(**{"citizen_service_number": citizen_service_number})
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate BSN data: {exc}") from exc

        # Set the correct Accept header for API version 2018-01-01
        headers = {
            "Accept": "application/json;version=2018-01-01",
            "Content-Type": "application/json"
        }

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/employees/{employee_id}/citizenservicenumber",
            json=request_body,
            headers=headers,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def create(
        self,
        employer_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create a new employee for a specific employer using flat payload input.

        Args:
            employer_id: The unique identifier of the employer
            data: Flat dictionary containing employee creation data

        Returns:
            Response: API response from the create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            # Flat data input
            data = {
                "employee_number": 156,
                "first_name": "John",
                "last_name": "Doe",
                "initials": "J.D.",
                "date_of_birth": "1990-01-01",
                "email_address": "john.doe@example.com",
                "start_date": "2024-01-01",
                # ... other fields
            }
            response = loket.employees.create("employer_id", data)
        """
        try:
            # fold_flat_keys handles complete structure with camelCase aliases
            # Pydantic validation with populate_by_name=True accepts the structure
            # model_dump completes any remaining alias conversions
            validated_data = EmployeeCreate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise Exception(f"Failed to validate employee create data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/{employer_id}/employee",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response
