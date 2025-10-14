from typing import Dict, Any, Optional, Tuple
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.social_security_benefits import SocialSecurityBenefitsGet, SocialSecurityBenefitsCreate, SocialSecurityBenefitsUpdate


class SocialSecurityBenefits:
    """
    Handles social security benefits GET and CREATE operations for Loket SDK.
    """

    def __init__(self, loket):
        """
        Initialize the SocialSecurityBenefits class.

        Args:
            loket: The Loket SDK instance
        """
        self.loket = loket

    def get(
        self,
        employment_id: Optional[str] = None,
        social_security_benefits_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get social security benefits data. Can retrieve either a list of social security benefits for an employment or a specific social security benefit by ID.

        Args:
            employment_id: The unique identifier of the employment (for getting all social security benefits)
            social_security_benefits_id: The unique identifier of the social security benefit (for getting specific social security benefit)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated social security benefits data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all social security benefits for an employment
            valid_df, invalid_df = loket.social_security_benefits.get(employment_id="xxx-xxx")

            # Get specific social security benefit by ID
            valid_df, invalid_df = loket.social_security_benefits.get(social_security_benefits_id="yyy-yyy")

            # Get social security benefits with filter (active only)
            valid_df, invalid_df = loket.social_security_benefits.get(employment_id="xxx-xxx", filter_query="isActive eq true")
        """
        try:
            # Determine endpoint and parameters based on input
            if social_security_benefits_id:
                # Get specific social security benefit by ID
                endpoint = f"providers/employers/employees/employments/socialsecuritybenefits/{social_security_benefits_id}"
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
                # Get all social security benefits for employment
                endpoint = f"providers/employers/employees/employments/{employment_id}/socialsecuritybenefits"
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
                raise ValueError("Either employment_id or social_security_benefits_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, SocialSecurityBenefitsGet)

            return valid_data, invalid_data

        except Exception as e:
            if social_security_benefits_id:
                raise ValueError(f"Failed to get social security benefit {social_security_benefits_id}: {e}")
            else:
                raise ValueError(f"Failed to get social security benefits for employment {employment_id}: {e}")

    def create(
        self,
        employment_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create a new social security benefit for a specific employment using flat or nested payload input.

        Args:
            employment_id: The unique identifier of the employment
            data: Dictionary containing social security benefit data (flat or nested structure accepted)

        Returns:
            Response: API response from the create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            # Flat data input
            data = {
                "start_date": "2018-01-01",
                "end_date": "2018-10-23",
                "supplementation": {"type": {"key": 3}, "percentage": 35},
                "benefit": {"type": {}, "percentage": 35}
            }
            response = loket.social_security_benefits.create(employment_id="xxx-xxx", data=data)
        """
        try:
            # Validate input data using Pydantic schema (handles flat-to-nested conversion)
            validated_data = SocialSecurityBenefitsCreate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise Exception(f"Failed to validate social security benefits create data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/socialsecuritybenefits",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update(
        self,
        social_security_benefit_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update an existing social security benefit using flat or nested payload input.

        Args:
            social_security_benefit_id: The unique identifier of the social security benefit
            data: Dictionary containing social security benefit data to update (flat or nested structure accepted)

        Returns:
            Response: API response from the update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            # Nested data input
            data = {
                "start_date": "2018-01-01",
                "end_date": "2018-10-23",
                "supplementation": {"type": {"key": 3}, "percentage": 35},
                "benefit": {"percentage": 35}
            }
            response = loket.social_security_benefits.update(
                social_security_benefit_id="xxx-xxx",
                data=data
            )
        """
        try:
            # Validate input data using Pydantic schema (handles flat-to-nested conversion)
            validated_data = SocialSecurityBenefitsUpdate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise Exception(f"Failed to validate social security benefits update data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/socialsecuritybenefits/{social_security_benefit_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def delete(
        self,
        social_security_benefits_id: str,
    ) -> Response:
        """
        Delete an existing social security benefit.

        Args:
            social_security_benefits_id: The unique identifier of the social security benefit

        Returns:
            Response: API response from the delete request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the request fails

        Example:
            response = loket.social_security_benefits.delete(social_security_benefits_id="xxx-xxx")
        """
        try:
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/socialsecuritybenefits/{social_security_benefits_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to delete social security benefit {social_security_benefits_id}: {e}")
