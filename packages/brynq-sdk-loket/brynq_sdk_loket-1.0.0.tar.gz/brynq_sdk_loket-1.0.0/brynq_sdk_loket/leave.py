"""
Leave resource class for Loket SDK.

This module provides methods for interacting with employment leave-related endpoints
in the Loket API, including retrieving leave information.
"""

from typing import Optional, Tuple, Dict, Any, List
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions as BrynQFunctions
from .schemas.leave import LeaveGet, LeaveUpdate, LeaveImportDataGet, LeaveBatchCreate


class Leave:
    """
    Handles all leave-related operations for Loket SDK.

    This class provides methods to interact with employment leave endpoints,
    including retrieving leave information.
    """

    def __init__(self, loket_instance):
        """
        Initialize the Leave resource.

        Args:
            loket_instance: The Loket client instance
        """
        self.loket = loket_instance

    def get(self, leave_id: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get leave data by ID.

        Args:
            leave_id: The unique identifier of the leave

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)

        Example:
            valid_df, invalid_df = loket.leave.get(leave_id="xxx-xxx")
        """
        try:
            if not leave_id.strip():
                raise ValueError("Leave ID cannot be empty")

            # Get specific leave by ID
            endpoint = f"providers/employers/employees/employments/leave/{leave_id}"
            response_data = self.loket.get(
                endpoint=endpoint,
                get_all_pages=False
            )

            # Convert to DataFrame for validation
            if not response_data:
                return pd.DataFrame(), pd.DataFrame()

            # Extract content from response (get_by_id returns content object)
            if "content" in response_data:
                leave_data = response_data["content"]
            else:
                leave_data = response_data

            # Normalize nested JSON structure (single item in list)
            df = pd.json_normalize([leave_data])

            if df.empty:
                return pd.DataFrame(), pd.DataFrame()

            valid_data, invalid_data = BrynQFunctions.validate_data(df, LeaveGet)

            return valid_data, invalid_data

        except Exception as e:
            raise Exception(f"Failed to get leave {leave_id}: {e}")

    def update(self, leave_id: str, data: Dict[str, Any]) -> Response:
        """
        Update an existing leave.

        Args:
            leave_id: The unique identifier of the leave to update
            data: Leave data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the leave data is invalid

        Example:
            # Update leave with flat data structure
            response = loket.leave.update(
                leave_id="xxx-xxx",
                data={
                    "number_of_units": 8,
                    "is_accrual": False,
                    "start_date": "2017-11-01",
                    "end_date": "2017-11-01",
                    "leave_type_key": 1,
                    "comment": "some comment"
                }
            )
        """
        try:
            # Validate and convert flat data to nested structure
            leave_data = LeaveUpdate(**data)
            request_body = leave_data.model_dump(by_alias=True, exclude_none=True)
            # Make PUT request to update leave
            response = self.loket.session.put(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/leave/{leave_id}",
                json=request_body,
                timeout=self.loket.timeout,
            )
            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to update leave {leave_id}: {e}")

    def delete(self, leave_id: str) -> Response:
        """
        Delete a leave by ID.

        Args:
            leave_id: The unique identifier of the leave

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the leave ID is invalid

        Example:
            # Delete leave
            response = loket.leave.delete(leave_id="xxx-xxx")
        """
        if not leave_id or not leave_id.strip():
            raise ValueError("Leave ID cannot be empty")

        try:
            # Make DELETE request to delete leave
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/leave/{leave_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to delete leave {leave_id}: {e}")

    def get_import_data(self, employer_id: str, filter_query: Optional[str] = None, order_by: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get leave import data for an employer.

        Args:
            employer_id: The unique identifier of the employer
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)

        Example:
            # Get leave import data for an employer
            valid_df, invalid_df = loket.leave.get_import_data(employer_id="xxx-xxx")
        """
        try:
            if not employer_id.strip():
                raise ValueError("Employer ID cannot be empty")

            # Get leave import data for employer
            endpoint = f"providers/employers/{employer_id}/import/leave"
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

            if df.empty:
                return pd.DataFrame(), pd.DataFrame()

            # For import data, we don't need complex validation, just return the data
            valid_data, invalid_data = BrynQFunctions.validate_data(df, LeaveImportDataGet)
            return valid_data, invalid_data

        except Exception as e:
            raise Exception(f"Failed to get leave import data for employer {employer_id}: {e}")

    def import_csv(self, employer_id: str, data_base64: str, mime_type: str = "text/csv") -> Response:
        """
        Import leave data via CSV for a given employer.

        Args:
            employer_id: Employer identifier
            data_base64: Base64-encoded CSV content
            mime_type: MIME type of the payload (default: text/csv)

        Returns:
            Response: The HTTP response from the API
        """
        if not employer_id or not employer_id.strip():
            raise ValueError("Employer ID cannot be empty")
        if not data_base64 or not isinstance(data_base64, str):
            raise ValueError("data_base64 must be a non-empty base64 string")

        try:
            payload = {"mimeType": mime_type, "data": data_base64}
            response = self.loket.session.post(
                url=f"{self.loket.base_url}/providers/employers/{employer_id}/import/leave",
                json=payload,
                timeout=self.loket.timeout,
            )
            response.raise_for_status()
            return response
        except Exception as e:
            raise Exception(f"Failed to import leave CSV for employer {employer_id}: {e}")

    def create_batch(self, employer_id: str, data: List[Dict[str, Any]]) -> Response:
        """
        Create leave for multiple employments in batch.

        This endpoint creates leave records for multiple employments at once.
        Each item in the data list represents a leave record to be created.

        Args:
            employer_id: The unique identifier of the employer
            data: List of dictionaries containing leave data for multiple employments

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            # Create leave for multiple employments
            leave_data = [
                {
                    "employment_id": "emp-123",
                    "start_date": "2022-10-21",
                    "end_date": "2022-10-22",
                    "leave_type_key": 1,
                    "is_accrual": True,
                    "number_of_units": 4.5,
                    "comments": "This leave is added."
                },
                {
                    "employment_id": "emp-456",
                    "start_date": "2022-10-25",
                    "end_date": "2022-10-25",
                    "leave_type_key": 2,
                    "is_accrual": False,
                    "number_of_units": 8.0,
                    "comments": "Another leave record."
                }
            ]
            response = loket.leave.create_batch(employer_id="xxx-xxx", data=leave_data)
        """
        if not employer_id or not employer_id.strip():
            raise ValueError("Employer ID cannot be empty")
        if not data or not isinstance(data, list):
            raise ValueError("Data must be a non-empty list of dictionaries")

        try:
            # Validate each item in the batch
            validated_data = []
            for item in data:
                if not isinstance(item, dict):
                    raise ValueError("Each item in data must be a dictionary")

                # Validate input data using Pydantic schema
                validated_item = LeaveBatchCreate(**item)
                validated_data.append(validated_item.model_dump(by_alias=True, mode="json", exclude_none=True))


        except Exception as exc:
            raise ValueError(f"Failed to validate leave batch create data: {exc}")

        # Make POST request to create leave in batch
        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/{employer_id}/leave",
            json=validated_data,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response
