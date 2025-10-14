"""
WorkingHours resource class for Loket SDK.

This module provides methods for interacting with employment working hours-related endpoints
in the Loket API, including retrieving working hours information.
"""

from typing import Optional, Tuple, Dict, Any
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions as BrynQFunctions
from .schemas.working_hours import WorkingHoursGet, WorkingHoursCreate


class WorkingHours:
    """
    Handles all working hours-related operations for Loket SDK.

    This class provides methods to interact with employment working hours endpoints,
    including retrieving working hours information.
    """

    def __init__(self, loket_instance):
        """
        Initialize the WorkingHours resource.

        Args:
            loket_instance: The Loket client instance
        """
        self.loket = loket_instance

    def get(self, employment_id: Optional[str] = None, working_hours_id: Optional[str] = None, filter_query: Optional[str] = None, order_by: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get working hours data. Can retrieve either a list of working hours for an employment or a specific working hours by ID.

        Args:
            employment_id: The unique identifier of the employment (for getting all working hours)
            working_hours_id: The unique identifier of the working hours (for getting specific working hours)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated working hours data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all working hours for an employment
            valid_df, invalid_df = loket.working_hours.get(employment_id="xxx-xxx")

            # Get specific working hours by ID
            valid_df, invalid_df = loket.working_hours.get(working_hours_id="yyy-yyy")

            # Get working hours with filter (regular work pattern equals true)
            valid_df, invalid_df = loket.working_hours.get(employment_id="xxx-xxx", filter_query="regularWorkPattern eq true")
        """
        try:
            # Determine endpoint and parameters based on input
            if working_hours_id:
                if not working_hours_id.strip():
                    raise ValueError("Working hours ID cannot be empty")

                # Get specific working hours by ID
                endpoint = f"providers/employers/employees/employments/workinghours/{working_hours_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Extract content from response (get_by_id returns content object)
                if "content" in response_data:
                    working_hours_data = response_data["content"]
                else:
                    working_hours_data = response_data

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([working_hours_data])

            elif employment_id:
                # Get all working hours for employment
                endpoint = f"providers/employers/employees/employments/{employment_id}/workinghours"
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
                raise ValueError("Either employment_id or working_hours_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = BrynQFunctions.validate_data(df, WorkingHoursGet)

            return valid_data, invalid_data

        except Exception as e:
            if working_hours_id:
                raise Exception(f"Failed to get working hours {working_hours_id}: {e}")
            else:
                raise Exception(f"Failed to get working hours for employment {employment_id}: {e}")

    def create(self, employment_id: str, data: Dict[str, Any]) -> Response:
        """
        Create new working hours for an employment.

        Args:
            employment_id: The unique identifier of the employment
            data: Working hours data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the working hours data is invalid

        Example:
            # Create working hours with flat data structure
            response = loket.working_hours.create(
                employment_id="xxx-xxx",
                data={
                    "start_date": "2018-01-01",
                    "shift_number": 1,
                    "deviating_hours_per_week": 32,
                    "average_hours_per_week": 32,
                    "deviating_sv_days_per_period": 20,
                    "average_parttime_factor": 37.5,
                    "regular_work_pattern": True,
                    "shift_rate_sick_leave_number": 1,
                    "flexible_hours_contract_key": 2,
                    "work_pattern_odd_monday": 8,
                    "work_pattern_odd_tuesday": 8,
                    "work_pattern_odd_wednesday": 4,
                    "work_pattern_odd_thursday": 7.5,
                    "work_pattern_odd_friday": 4,
                    "work_pattern_odd_saturday": 0,
                    "work_pattern_odd_sunday": 0,
                    "work_pattern_even_monday": 0,
                    "work_pattern_even_tuesday": 8,
                    "work_pattern_even_wednesday": 8,
                    "work_pattern_even_thursday": 8,
                    "work_pattern_even_friday": 2,
                    "work_pattern_even_saturday": 0,
                    "work_pattern_even_sunday": 0,
                    "calculate_leave_hours": True,
                    "calculate_hours_broken_period": False,
                    "calculate_hours_regular_period": False,
                    "calculate_days_daily_rate": False,
                    "calculate_deviating_days_hours": False,
                    "contract_code_key": "b14acd0d-75d7-4fc8-8b22-4a3924585cab"
                }
            )
        """
        if not employment_id or not employment_id.strip():
            raise ValueError("Employment ID cannot be empty")

        try:
            # Validate and convert flat data to nested structure
            working_hours_data = WorkingHoursCreate(**data)
            request_body = working_hours_data.model_dump(by_alias=True, exclude_none=True)
            # Make POST request to create working hours
            response = self.loket.session.post(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/workinghours",
                json=request_body,
                timeout=self.loket.timeout,
            )
            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to create working hours for employment {employment_id}: {e}")

    def update(self, working_hours_id: str, data: Dict[str, Any]) -> Response:
        """
        Update working hours by ID.

        Args:
            working_hours_id: The unique identifier of the working hours
            data: Working hours data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the working hours data is invalid

        Example:
            # Update working hours with flat data structure
            response = loket.working_hours.update(
                working_hours_id="xxx-xxx",
                data={
                    "start_date": "2018-01-01",
                    "shift_number": 1,
                    "deviating_hours_per_week": 32,
                    "average_hours_per_week": 32,
                    "deviating_sv_days_per_period": 20,
                    "average_parttime_factor": 37.5,
                    "regular_work_pattern": True,
                    "shift_rate_sick_leave_number": 1,
                    "flexible_hours_contract_key": 2,
                    "work_pattern_odd_monday": 8,
                    "work_pattern_odd_tuesday": 8,
                    "work_pattern_odd_wednesday": 4,
                    "work_pattern_odd_thursday": 7.5,
                    "work_pattern_odd_friday": 4,
                    "work_pattern_odd_saturday": 0,
                    "work_pattern_odd_sunday": 0,
                    "work_pattern_even_monday": 0,
                    "work_pattern_even_tuesday": 8,
                    "work_pattern_even_wednesday": 8,
                    "work_pattern_even_thursday": 8,
                    "work_pattern_even_friday": 2,
                    "work_pattern_even_saturday": 0,
                    "work_pattern_even_sunday": 0,
                    "calculate_leave_hours": True,
                    "calculate_hours_broken_period": False,
                    "calculate_hours_regular_period": False,
                    "calculate_days_daily_rate": False,
                    "calculate_deviating_days_hours": False,
                    "contract_code_key": "b14acd0d-75d7-4fc8-8b22-4a3924585cab"
                }
            )
        """
        if not working_hours_id or not working_hours_id.strip():
            raise ValueError("Working hours ID cannot be empty")

        try:
            # Validate and convert flat data to nested structure
            working_hours_data = WorkingHoursCreate(**data)
            request_body = working_hours_data.model_dump(by_alias=True, exclude_none=True)

            # Make PUT request to update working hours
            response = self.loket.session.put(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/workinghours/{working_hours_id}",
                json=request_body,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to update working hours {working_hours_id}: {e}")

    def delete(self, working_hours_id: str) -> Response:
        """
        Delete working hours by ID.

        Args:
            working_hours_id: The unique identifier of the working hours

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the working hours ID is invalid

        Example:
            # Delete working hours
            response = loket.working_hours.delete(working_hours_id="xxx-xxx")
        """
        if not working_hours_id or not working_hours_id.strip():
            raise ValueError("Working hours ID cannot be empty")

        try:
            # Make DELETE request to delete working hours
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/workinghours/{working_hours_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to delete working hours {working_hours_id}: {e}")
