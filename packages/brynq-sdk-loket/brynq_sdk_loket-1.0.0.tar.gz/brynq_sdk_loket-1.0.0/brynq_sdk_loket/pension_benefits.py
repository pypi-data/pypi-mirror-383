from typing import Dict, Any, Optional, Tuple
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.pension_benefits import PensionBenefitsGet, PensionBenefitsCreate, PensionBenefitsUpdate


class PensionBenefits:
    """
    Handles all pension benefits-related operations for Loket SDK.

    This class provides methods to interact with pension benefits data,
    including retrieving, creating, updating, and deleting pension benefits.
    """

    def __init__(self, loket):
        """
        Initialize the PensionBenefits class.

        Args:
            loket: The Loket SDK instance
        """
        self.loket = loket

    def get(
        self,
        employment_id: Optional[str] = None,
        pension_benefits_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get pension benefits data. Can retrieve either a list of pension benefits for an employment or a specific pension benefit by ID.

        Args:
            employment_id: The unique identifier of the employment (for getting all pension benefits)
            pension_benefits_id: The unique identifier of the pension benefit (for getting specific pension benefit)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated pension benefits data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all pension benefits for an employment
            valid_df, invalid_df = loket.pension_benefits.get(employment_id="xxx-xxx")

            # Get specific pension benefit by ID
            valid_df, invalid_df = loket.pension_benefits.get(pension_benefits_id="yyy-yyy")

            # Get pension benefits with filter (active only)
            valid_df, invalid_df = loket.pension_benefits.get(employment_id="xxx-xxx", filter_query="isActive eq true")
        """
        try:
            # Determine endpoint and parameters based on input
            if pension_benefits_id:
                # Get specific pension benefit by ID
                endpoint = f"providers/employers/employees/employments/pensionbenefits/{pension_benefits_id}"
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
                # Get all pension benefits for employment
                endpoint = f"providers/employers/employees/employments/{employment_id}/pensionbenefits"
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
                raise ValueError("Either employment_id or pension_benefits_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, PensionBenefitsGet)

            return valid_data, invalid_data

        except Exception as e:
            if pension_benefits_id:
                raise ValueError(f"Failed to get pension benefit {pension_benefits_id}: {e}")
            else:
                raise ValueError(f"Failed to get pension benefits for employment {employment_id}: {e}")

    def create(
        self,
        employment_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create a new pension benefit for a specific employment.

        Args:
            employment_id: The unique identifier of the employment
            data: Dictionary containing pension benefit data

        Returns:
            Response: API response from the create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "start_date": "2018-01-01",
                "payout": 2569
            }
            response = loket.pension_benefits.create(employment_id="xxx-xxx", data=data)
        """
        try:
            # Convert flat data to nested structure using alias mapping
            nested_data = self.loket.flat_dict_to_nested_dict(data, PensionBenefitsCreate)
            # Validate input data using Pydantic schema
            validated_data = PensionBenefitsCreate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate pension benefits create data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/pensionbenefits",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update(
        self,
        pension_benefits_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update an existing pension benefit.

        Args:
            pension_benefits_id: The unique identifier of the pension benefit
            data: Dictionary containing pension benefit data to update

        Returns:
            Response: API response from the update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "start_date": "2018-01-01",
                "payout": 2569
            }
            response = loket.pension_benefits.update(
                pension_benefits_id="xxx-xxx",
                data=data
            )
        """
        try:
            # Convert flat data to nested structure using alias mapping
            nested_data = self.loket.flat_dict_to_nested_dict(data, PensionBenefitsUpdate)
            # Validate input data using Pydantic schema
            validated_data = PensionBenefitsUpdate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate pension benefits update data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/pensionbenefits/{pension_benefits_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def delete(
        self,
        pension_benefits_id: str,
    ) -> Response:
        """
        Delete an existing pension benefit.

        Args:
            pension_benefits_id: The unique identifier of the pension benefit

        Returns:
            Response: API response from the delete request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the request fails

        Example:
            response = loket.pension_benefits.delete(pension_benefits_id="xxx-xxx")
        """
        try:
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/pensionbenefits/{pension_benefits_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to delete pension benefit {pension_benefits_id}: {e}")
