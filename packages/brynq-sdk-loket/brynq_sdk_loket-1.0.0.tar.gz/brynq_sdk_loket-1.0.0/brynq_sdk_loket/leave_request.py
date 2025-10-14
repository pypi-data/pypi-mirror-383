"""
LeaveRequest resource class for Loket SDK.
"""

from typing import Optional, Tuple, Dict, Any
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions as BrynQFunctions
from .schemas.leave_request import LeaveRequestGet, LeaveRequestCreate


class LeaveRequest:

    def __init__(self, loket_instance):
        self.loket = loket_instance

    def get(self, employer_id: Optional[str] = None, employment_id: Optional[str] = None, leave_request_id: Optional[str] = None, filter_query: Optional[str] = None, order_by: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get leave requests by employer, employment, or specific leave request ID.

        Args:
            employer_id: Get all leave requests for an employer
            employment_id: Get all leave requests for a specific employment
            leave_request_id: Get a specific leave request by ID
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
        """
        try:
            # Determine which endpoint to use based on provided parameters
            if leave_request_id:
                if not leave_request_id.strip():
                    raise ValueError("Leave request ID cannot be empty")
                endpoint = f"providers/employers/employees/employments/leaverequests/{leave_request_id}"
                response_data = self.loket.get(endpoint=endpoint, get_all_pages=False)

                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Extract content from response (get_by_id returns content object)
                if "content" in response_data:
                    leave_request_data = response_data["content"]
                else:
                    leave_request_data = response_data

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([leave_request_data])

            elif employment_id:
                if not employment_id.strip():
                    raise ValueError("Employment ID cannot be empty")
                endpoint = f"providers/employers/employees/employments/{employment_id}/leaverequests"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    filter_query=filter_query,
                    order_by=order_by,
                    get_all_pages=True,
                )

                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                df = pd.json_normalize(response_data)

            elif employer_id:
                if not employer_id.strip():
                    raise ValueError("Employer ID cannot be empty")
                endpoint = f"providers/employers/{employer_id}/employees/employments/leaverequests"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    filter_query=filter_query,
                    order_by=order_by,
                    get_all_pages=True,
                )

                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                df = pd.json_normalize(response_data)

            else:
                raise ValueError("Either employer_id, employment_id, or leave_request_id must be provided")

            if df.empty:
                return pd.DataFrame(), pd.DataFrame()

            valid_data, invalid_data = BrynQFunctions.validate_data(df, LeaveRequestGet)
            return valid_data, invalid_data

        except Exception as e:
            if leave_request_id:
                raise Exception(f"Failed to get leave request {leave_request_id}: {e}")
            elif employment_id:
                raise Exception(f"Failed to get leave requests for employment {employment_id}: {e}")
            else:
                raise Exception(f"Failed to get leave requests for employer {employer_id}: {e}")

    def create(self, employment_id: str, data: Dict[str, Any]) -> Response:
        """
        Create a new leave request for an employment.

        Args:
            employment_id: The unique identifier of the employment
            data: Leave request data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Example:
            response = loket.leave_request.create(
                employment_id="xxx-xxx",
                data={
                    "number_of_units": 8,
                    "is_accrual": False,
                    "start_date": "2017-11-01",
                    "end_date": "2017-11-01",
                    "leave_type_key": 1,
                    "comment_employee": "Vakantie naar Spanje",
                    "started_via_workflow": True
                }
            )
        """
        if not employment_id or not employment_id.strip():
            raise ValueError("Employment ID cannot be empty")

        try:
            # Validate and convert flat data to nested structure
            leave_request_data = LeaveRequestCreate(**data)
            request_body = leave_request_data.model_dump(by_alias=True, exclude_none=True)
            # Make POST request to create leave request
            response = self.loket.session.post(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/leaverequests",
                json=request_body,
                timeout=self.loket.timeout,
            )
            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to create leave request for employment {employment_id}: {e}")

    def update(self, leave_request_id: str, data: Dict[str, Any]) -> Response:
        """
        Update an existing leave request.

        Args:
            leave_request_id: The unique identifier of the leave request to update
            data: Leave request data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Example:
            response = loket.leave_request.update(
                leave_request_id="xxx-xxx",
                data={
                    "number_of_units": 8,
                    "is_accrual": False,
                    "start_date": "2017-11-01",
                    "end_date": "2017-11-01",
                    "leave_type_key": 1,
                    "comment_handler": "Fijne vakantie!"
                }
            )
        """
        if not leave_request_id or not leave_request_id.strip():
            raise ValueError("Leave request ID cannot be empty")

        try:
            # Validate and convert flat data to nested structure
            leave_request_data = LeaveRequestCreate(**data)
            request_body = leave_request_data.model_dump(by_alias=True, exclude_none=True)
            # Make PUT request to update leave request
            response = self.loket.session.put(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/leaverequests/{leave_request_id}",
                json=request_body,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to update leave request {leave_request_id}: {e}")

    def change_status(self, leave_request_actions: list) -> Response:
        """
        Change status of leave requests (accept/reject).

        Args:
            leave_request_actions: List of dictionaries with 'id' and 'action' keys
                                  Example: [{"id": "xxx-xxx", "action": "accept"}]

        Returns:
            Response: The HTTP response from the API

        Example:
            response = loket.leave_request.change_status([
                {"id": "b14acd0d-75d7-4fc8-8b22-4a3924585cab", "action": "accept"}
            ])
        """
        if not leave_request_actions or not isinstance(leave_request_actions, list):
            raise ValueError("leave_request_actions must be a non-empty list")

        try:
            # Make PATCH request to change leave request status
            response = self.loket.session.patch(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/leaverequests",
                json=leave_request_actions,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to change leave request status: {e}")
