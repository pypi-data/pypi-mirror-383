"""
LeaveType resource class for Loket SDK.
"""

from typing import Optional, Tuple, Dict, Any
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions as BrynQFunctions
from .schemas.leave_type import LeaveTypeGet, LeaveTypeUpdate


class LeaveTypes:
    def __init__(self, loket_instance):
        self.loket = loket_instance

    def get(self, employer_id: str, leave_type_id: Optional[str] = None, filter_query: Optional[str] = None, order_by: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get leave types by employer or specific leave type ID.

        Args:
            employer_id: Get all leave types for an employer (mandatory)
            leave_type_id: Get a specific leave type by ID (optional)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
        """
        try:
            # Validate mandatory employer_id
            if not employer_id or not employer_id.strip():
                raise ValueError("Employer ID is mandatory and cannot be empty")

            # Determine which endpoint to use based on provided parameters
            if leave_type_id:
                if not leave_type_id.strip():
                    raise ValueError("Leave type ID cannot be empty")
                endpoint = f"providers/employers/{employer_id}/leavetypes/{leave_type_id}"
                response_data = self.loket.get(endpoint=endpoint, get_all_pages=False)

                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Extract content from response (get_by_id returns content object)
                if "content" in response_data:
                    leave_type_data = response_data["content"]
                else:
                    leave_type_data = response_data

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([leave_type_data])

            else:
                # Get all leave types for employer
                endpoint = f"providers/employers/{employer_id}/leavetypes"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    filter_query=filter_query,
                    order_by=order_by,
                    get_all_pages=True,
                )

                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                df = pd.json_normalize(response_data)

            if df.empty:
                return pd.DataFrame(), pd.DataFrame()

            valid_data, invalid_data = BrynQFunctions.validate_data(df, LeaveTypeGet)
            return valid_data, invalid_data

        except Exception as e:
            if leave_type_id:
                raise Exception(f"Failed to get leave type {leave_type_id}: {e}")
            else:
                raise Exception(f"Failed to get leave types for employer {employer_id}: {e}")

    def update(self, employer_id: str, leave_type_id: str, data: Dict[str, Any]) -> Response:
        """
        Update an existing leave type.

        Args:
            employer_id: The unique identifier of the employer
            leave_type_id: The unique identifier of the leave type to update
            data: Leave type data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Example:
            response = loket.leave_types.update(
                employer_id="xxx-xxx",
                leave_type_id="yyy-yyy",
                data={
                    "deviations_value": "Verlof",
                    "deviations_balance_exceeds_year": True,
                    "deviations_enabled": True,
                    "deviations_employee_can_request_increase": False
                }
            )
        """
        if not employer_id or not employer_id.strip():
            raise ValueError("Employer ID cannot be empty")
        if not leave_type_id or not leave_type_id.strip():
            raise ValueError("Leave type ID cannot be empty")

        try:
            # Validate input data
            leave_type_data = LeaveTypeUpdate(**data)

            request_body = leave_type_data.model_dump(mode="json", by_alias=True, exclude_none=True)
            request_body = {"deviations": request_body}

            # Make PUT request to update leave type
            response = self.loket.session.put(
                url=f"{self.loket.base_url}/providers/employers/{employer_id}/leavetypes/{leave_type_id}",
                json=request_body,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to update leave type {leave_type_id} for employer {employer_id}: {e}")
