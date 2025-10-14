from typing import Dict, Any, Optional, Tuple
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.absence_progress import AbsenceProgressGet, AbsenceProgressCreate, AbsenceProgressUpdate


class AbsenceProgress:
    """
    Handles all absence progress-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize AbsenceProgress manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance

    def get(
        self,
        absence_id: Optional[str] = None,
        absence_progress_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get absence progress data. Can retrieve either a list of absence progress records for an absence or a specific absence progress by ID.

        Args:
            absence_id: The unique identifier of the absence (for getting all absence progress records)
            absence_progress_id: The unique identifier of the absence progress (for getting specific absence progress)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated absence progress data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all absence progress records for an absence
            valid_df, invalid_df = loket.absence_progress.get(absence_id="xxx-xxx")

            # Get specific absence progress by ID
            valid_df, invalid_df = loket.absence_progress.get(absence_progress_id="yyy-yyy")

            # Get absence progress with filter (status equals 'Completed')
            valid_df, invalid_df = loket.absence_progress.get(absence_id="xxx-xxx", filter_query="status eq 'Completed'")
        """
        try:
            # Determine endpoint and parameters based on input
            if absence_progress_id:
                # Get specific absence progress by ID
                endpoint = f"providers/employers/employees/absences/absenceprogress/{absence_progress_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([response_data.get("content")])

            elif absence_id:
                # Get all absence progress records for absence
                endpoint = f"providers/employers/employees/absences/{absence_id}/absenceprogress"
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
                raise ValueError("Either absence_id or absence_progress_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, AbsenceProgressGet)

            return valid_data, invalid_data

        except Exception as e:
            if absence_progress_id:
                raise ValueError(f"Failed to get absence progress {absence_progress_id}: {e}")
            else:
                raise ValueError(f"Failed to get absence progress for absence {absence_id}: {e}")

    def create(
        self,
        absence_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create a new absence progress for a specific absence using flat or nested payload input.

        Args:
            absence_id: The unique identifier of the absence
            data: Dictionary containing absence progress data (flat or nested structure accepted)

        Returns:
            Response: API response from the create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            # Flat data input
            data = {
                "start_date": "2018-01-21",
                "incapacity_percentage": 100,
                "type_of_work_resumption": {"key": 2},
                "comments": "Lorem ipsum dolor sit amet"
            }
            response = loket.absence_progress.create(absence_id="xxx-xxx", data=data)
        """
        try:
            # Convert flat data to nested structure using alias mapping
            nested_data = self.loket.flat_dict_to_nested_dict(data, AbsenceProgressCreate)
            # Validate input data using Pydantic schema
            validated_data = AbsenceProgressCreate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate absence progress create data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/employees/absences/{absence_id}/absenceprogress",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update(
        self,
        absence_progress_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update an existing absence progress using flat or nested payload input.

        Args:
            absence_progress_id: The unique identifier of the absence progress
            data: Dictionary containing absence progress data to update (flat or nested structure accepted)

        Returns:
            Response: API response from the update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            # Flat data input
            data = {
                "start_date": "2018-01-21",
                "incapacity_percentage": 100,
                "type_of_work_resumption": {"key": 2},
                "comments": "Updated comment"
            }
            response = loket.absence_progress.update(
                absence_progress_id="xxx-xxx",
                data=data
            )
        """
        try:
            # Convert flat data to nested structure using alias mapping
            nested_data = self.loket.flat_dict_to_nested_dict(data, AbsenceProgressUpdate)
            # Validate input data using Pydantic schema
            validated_data = AbsenceProgressUpdate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate absence progress update data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/employees/absences/absenceprogress/{absence_progress_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def delete(
        self,
        absence_progress_id: str,
    ) -> Response:
        """
        Delete an existing absence progress.

        Args:
            absence_progress_id: The unique identifier of the absence progress

        Returns:
            Response: API response from the delete request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the request fails

        Example:
            response = loket.absence_progress.delete(absence_progress_id="xxx-xxx")
        """
        try:
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/absences/absenceprogress/{absence_progress_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to delete absence progress {absence_progress_id}: {e}")
