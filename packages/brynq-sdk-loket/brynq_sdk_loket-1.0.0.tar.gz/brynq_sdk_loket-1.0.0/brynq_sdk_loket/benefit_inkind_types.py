from typing import Dict, Any, Optional, Tuple
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.benefit_inkind_types import BenefitInKindTypesGet, BenefitInKindTypesCreate, BenefitInKindTypesUpdate


class BenefitInKindTypes:
    """
    Handles all benefit in kind types-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize BenefitInKindTypes manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance

    def get(
        self,
        employer_id: Optional[str] = None,
        benefit_inkind_type_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get benefit in kind types data. Can retrieve either a list of benefit in kind types for an employer or a specific benefit in kind type by ID.

        Args:
            employer_id: The unique identifier of the employer (for getting all benefit in kind types)
            benefit_inkind_type_id: The unique identifier of the benefit in kind type (for getting specific benefit in kind type)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated benefit in kind types data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all benefit in kind types for an employer
            valid_df, invalid_df = loket.benefit_inkind_types.get(employer_id="xxx-xxx")

            # Get specific benefit in kind type by ID
            valid_df, invalid_df = loket.benefit_inkind_types.get(benefit_inkind_type_id="yyy-yyy")

            # Get benefit in kind types with filter (active only)
            valid_df, invalid_df = loket.benefit_inkind_types.get(employer_id="xxx-xxx", filter_query="isActive eq true")
        """
        try:
            # Determine endpoint and parameters based on input
            if benefit_inkind_type_id:
                # Get specific benefit in kind type by ID
                endpoint = f"providers/employers/benefitinkindtypes/{benefit_inkind_type_id}"
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
                # Get all benefit in kind types for employer
                endpoint = f"providers/employers/{employer_id}/benefitinkindtypes"
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
                raise ValueError("Either employer_id or benefit_inkind_type_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, BenefitInKindTypesGet)

            return valid_data, invalid_data

        except Exception as e:
            if benefit_inkind_type_id:
                raise ValueError(f"Failed to get benefit in kind type {benefit_inkind_type_id}: {e}")
            else:
                raise ValueError(f"Failed to get benefit in kind types for employer {employer_id}: {e}")

    def create(
        self,
        employer_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create a new benefit in kind type for a specific employer.

        Args:
            employer_id: The unique identifier of the employer
            data: Dictionary containing benefit in kind type data

        Returns:
            Response: API response from the create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "description": "Laptop"
            }
            response = loket.benefit_inkind_types.create(employer_id="xxx-xxx", data=data)
        """
        try:
            # Convert flat data to nested structure using alias mapping
            nested_data = self.loket.flat_dict_to_nested_dict(data, BenefitInKindTypesCreate)
            # Validate input data using Pydantic schema
            validated_data = BenefitInKindTypesCreate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate benefit in kind type create data: {exc}")

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/{employer_id}/benefitinkindtypes",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update(
        self,
        benefit_inkind_type_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Update an existing benefit in kind type.

        Args:
            benefit_inkind_type_id: The unique identifier of the benefit in kind type
            data: Dictionary containing benefit in kind type data to update

        Returns:
            Response: API response from the update request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            data = {
                "description": "Updated Laptop"
            }
            response = loket.benefit_inkind_types.update(
                benefit_inkind_type_id="xxx-xxx",
                data=data
            )
        """
        try:
            # Convert flat data to nested structure using alias mapping
            nested_data = self.loket.flat_dict_to_nested_dict(data, BenefitInKindTypesUpdate)
            # Validate input data using Pydantic schema
            validated_data = BenefitInKindTypesUpdate(**nested_data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate benefit in kind type update data: {exc}")

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/benefitinkindtypes/{benefit_inkind_type_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def delete(
        self,
        benefit_inkind_type_id: str,
    ) -> Response:
        """
        Delete an existing benefit in kind type.

        Args:
            benefit_inkind_type_id: The unique identifier of the benefit in kind type

        Returns:
            Response: API response from the delete request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the request fails

        Example:
            response = loket.benefit_inkind_types.delete(benefit_inkind_type_id="xxx-xxx")
        """
        try:
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/benefitinkindtypes/{benefit_inkind_type_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to delete benefit in kind type {benefit_inkind_type_id}: {e}")
