from typing import Dict, Any, Optional, Tuple
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.benefits_inkind import BenefitsInKindGet, BenefitsInKindCreate, BenefitsInKindUpdate


class BenefitsInKind:
    """
    Handles all benefits in kind-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize BenefitsInKind manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance

    def get(
        self,
        employment_id: Optional[str] = None,
        benefits_inkind_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get benefits in kind data. Can retrieve either a list of benefits in kind for an employment or a specific benefits in kind by ID.

        Args:
            employment_id: The unique identifier of the employment (for getting all benefits in kind)
            benefits_inkind_id: The unique identifier of the benefits in kind (for getting specific benefits in kind)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated benefits in kind data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all benefits in kind for an employment
            valid_df, invalid_df = loket.benefits_inkind.get(employment_id="xxx-xxx")

            # Get specific benefits in kind by ID
            valid_df, invalid_df = loket.benefits_inkind.get(benefits_inkind_id="yyy-yyy")

            # Get benefits in kind with filter (active only)
            valid_df, invalid_df = loket.benefits_inkind.get(employment_id="xxx-xxx", filter_query="isActive eq true")
        """
        try:
            # Determine endpoint and parameters based on input
            if benefits_inkind_id:
                # Get specific benefits in kind by ID
                endpoint = f"providers/employers/employees/employments/benefitsinkind/{benefits_inkind_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([response_data.get("content")])

            elif employment_id:
                # Get all benefits in kind for employment
                endpoint = f"providers/employers/employees/employments/{employment_id}/benefitsInKind"
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
                raise ValueError("Either employment_id or benefits_inkind_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, BenefitsInKindGet)

            return valid_data, invalid_data

        except Exception as e:
            if benefits_inkind_id:
                raise ValueError(f"Failed to get benefits in kind {benefits_inkind_id}: {e}")
            else:
                raise ValueError(f"Failed to get benefits in kind for employment {employment_id}: {e}")

    def create(
        self,
        employment_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create a new benefits in kind for a specific employment.

        Args:
            employment_id: The unique identifier of the employment
            data: Dictionary containing benefits in kind data

        Returns:
            Response: API response from the create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "start_date": "2018-01-01",
                "end_date": "2018-10-23",
                "benefit_inkind_type": {"id": "36530F13-59EB-4C15-B5F2-4F92B070A208"},
                "brand": "Apple",
                "type": "Iphone 11",
                "value": 1100,
                "supplier": "Mediamarkt",
                "particularities": "geen bijzonderheden"
            }
            response = loket.benefits_inkind.create(employment_id="xxx-xxx", data=data)
        """
        try:
            # Convert flat data to nested structure using alias mapping
            nested_data = self.loket.flat_dict_to_nested_dict(data, BenefitsInKindCreate)
            # Validate input data using Pydantic schema
            validated_data = BenefitsInKindCreate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate benefits in kind create data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/benefitsInKind",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update(
        self,
        benefits_inkind_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update an existing benefits in kind.

        Args:
            benefits_inkind_id: The unique identifier of the benefits in kind
            data: Dictionary containing benefits in kind data to update

        Returns:
            Response: API response from the update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "start_date": "2018-01-01",
                "end_date": "2018-10-23",
                "benefit_inkind_type": {"id": "36530F13-59EB-4C15-B5F2-4F92B070A208"},
                "brand": "Apple",
                "type": "Iphone 11",
                "value": 1100,
                "supplier": "Mediamarkt",
                "particularities": "geen bijzonderheden"
            }
            response = loket.benefits_inkind.update(
                benefits_inkind_id="xxx-xxx",
                data=data
            )
        """
        try:
            # Convert flat data to nested structure using alias mapping
            nested_data = self.loket.flat_dict_to_nested_dict(data, BenefitsInKindUpdate)
            # Validate input data using Pydantic schema
            validated_data = BenefitsInKindUpdate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate benefits in kind update data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/benefitsinkind/{benefits_inkind_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def delete(
        self,
        benefits_inkind_id: str,
    ) -> Response:
        """
        Delete an existing benefits in kind.

        Args:
            benefits_inkind_id: The unique identifier of the benefits in kind

        Returns:
            Response: API response from the delete request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the request fails

        Example:
            response = loket.benefits_inkind.delete(benefits_inkind_id="xxx-xxx")
        """
        try:
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/benefitsinkind/{benefits_inkind_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to delete benefits in kind {benefits_inkind_id}: {e}")
