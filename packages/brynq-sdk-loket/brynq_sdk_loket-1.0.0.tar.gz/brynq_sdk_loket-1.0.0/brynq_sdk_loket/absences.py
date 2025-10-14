from typing import Dict, Any, Optional, Tuple
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.absences import AbsenceGet, AbsenceCreate, AbsenceUpdate


class Absences:
    """
    Handles all absence-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize Absences manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance

    def get(
        self,
        employee_id: Optional[str] = None,
        absence_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get absences data. Can retrieve either a list of absences for an employee or a specific absence by ID.

        Args:
            employee_id: The unique identifier of the employee (for getting all absences)
            absence_id: The unique identifier of the absence (for getting specific absence)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated absence data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all absences for an employee
            valid_df, invalid_df = loket.absences.get(employee_id="xxx-xxx")

            # Get specific absence by ID (requires both employee_id and absence_id)
            valid_df, invalid_df = loket.absences.get(employee_id="xxx-xxx", absence_id="yyy-yyy")

            # Get absences with filter (status equals 'Approved')
            valid_df, invalid_df = loket.absences.get(employee_id="xxx-xxx", filter_query="status eq 'Approved'")
        """
        try:
            # Determine endpoint and parameters based on input
            if absence_id:
                if not employee_id:
                    raise ValueError("employee_id is required when getting specific absence by absence_id")

                # Get specific absence by ID
                endpoint = f"providers/employers/employees/{employee_id}/absences/{absence_id}"
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
                # Get all absences for employee
                endpoint = f"providers/employers/employees/{employee_id}/absences"
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
                raise ValueError("Either employee_id (for all absences) or employee_id + absence_id (for specific absence) must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, AbsenceGet)

            return valid_data, invalid_data

        except Exception as e:
            if absence_id:
                raise Exception(f"Failed to get absence {absence_id} for employee {employee_id}: {e}")
            else:
                raise Exception(f"Failed to get absences for employee {employee_id}: {e}")

    def create(
        self,
        employee_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create a new absence for a specific employee using flat or nested payload input.

        Args:
            employee_id: The unique identifier of the employee
            data: Dictionary containing absence data (flat or nested structure accepted)

        Returns:
            Response: API response from the create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            # Flat data input with _key suffix for MetadataWithKey fields
            data = {
                "cause_of_absence_key": 1,
                "hours_worked_on_first_day_of_absence": 3,
                "action_to_be_taken_by_occupational_health_and_safety_service_key": 1,
                "is_disrupted_employment_relationship": True,
                "is_work_related_illness": False,
                "is_recovered_within_two_weeks": False,
                "comments": "Sick leave",
                "contact_information_start_date": "2024-01-01",
                "contact_information_street": "Main St",
                "contact_information_city": "Amsterdam",
                "contact_information_house_number": 123,
                "contact_information_postal_code": "1000 AA",
                "contact_information_country_key": 530,
                # ... other fields
            }
            response = loket.employees.absences.create(employee_id="xxx-xxx", data=data)
        """
        try:
            # Validate input data using Pydantic schema
            # The fold_flat_keys validator will handle flat-to-nested conversion
            validated_data = AbsenceCreate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise Exception(f"Failed to validate absence create data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/employees/{employee_id}/absences",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update(
        self,
        employee_id: str,
        absence_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update an existing absence for a specific employee using flat or nested payload input.

        Args:
            employee_id: The unique identifier of the employee
            absence_id: The unique identifier of the absence
            data: Dictionary containing absence data to update (flat or nested structure accepted)

        Returns:
            Response: API response from the update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            # Flat data input
            data = {
                "cause_of_absence": {"key": 1},
                "comments": "Updated comment",
                "is_recovered_within_two_weeks": True,
            }
            response = loket.absences.update(
                employee_id="xxx-xxx",
                absence_id="yyy-yyy",
                data=data
            )
        """
        try:
            # Validate input data using Pydantic schema
            # The flat_to_nested_generic validator will handle flat-to-nested conversion
            validated_data = AbsenceUpdate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise Exception(f"Failed to validate absence update data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/employees/absences/{absence_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def delete(
        self,
        employee_id: str,
        absence_id: str,
    ) -> Response:
        """
        Delete an existing absence for a specific employee.

        Args:
            employee_id: The unique identifier of the employee
            absence_id: The unique identifier of the absence

        Returns:
            Response: API response from the delete request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the request fails

        Example:
            response = loket.absences.delete(employee_id="xxx-xxx", absence_id="yyy-yyy")
        """
        try:
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/absences/{absence_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to delete absence {absence_id} for employee {employee_id}: {e}")
