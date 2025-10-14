from typing import Optional, Tuple, Dict, Any
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.declarations import DeclarationGet, DeclarationCreate, DeclarationUpdate, DeclarationReviewItem, DeclarationProcessItem, DeclarationAuditTrailGet


class Declarations:
    """
    Handles all declaration-related operations for Loket SDK.
    """

    def __init__(self, loket_instance):
        """
        Initialize Declarations manager.

        Args:
            loket_instance: The parent Loket instance
        """
        self.loket = loket_instance

    def get(
        self,
        employment_id: Optional[str] = None,
        declaration_id: Optional[str] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get declarations data. Can retrieve either a list of declarations for an employment or a specific declaration by ID.

        Args:
            employment_id: The unique identifier of the employment (for getting all declarations or specific declaration)
            declaration_id: The unique identifier of the declaration (for getting specific declaration)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated declaration data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all declarations for an employment
            valid_df, invalid_df = loket.declarations.get(employment_id="xxx-xxx")

            # Get specific declaration by ID
            valid_df, invalid_df = loket.declarations.get(employment_id="xxx-xxx", declaration_id="yyy-yyy")

            # Get declarations with filter (status equals 'Submitted')
            valid_df, invalid_df = loket.declarations.get(employment_id="xxx-xxx", filter_query="status eq 'Submitted'")
        """
        try:
            # Determine endpoint and parameters based on input
            if declaration_id:
                if not employment_id:
                    raise ValueError("employment_id is required when getting specific declaration by declaration_id")
                # Get specific declaration by ID
                endpoint = f"providers/employers/employees/employments/{employment_id}/declarations/{declaration_id}"
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
                # Get all declarations for employment
                endpoint = f"providers/employers/employees/employments/{employment_id}/declarations"
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
                raise ValueError("Either employment_id (for all declarations) or employment_id + declaration_id (for specific declaration) must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, DeclarationGet)

            return valid_data, invalid_data

        except Exception as e:
            if declaration_id:
                raise ValueError(f"Failed to get declaration {declaration_id} for employment {employment_id}: {e}") from e
            else:
                raise ValueError(f"Failed to get declarations for employment {employment_id}: {e}") from e

    def get_audit_trail(
        self,
        declaration_id: str,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get the audit trail of a declaration.

        Args:
            declaration_id: The unique identifier of the declaration
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated audit trail data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            valid_df, invalid_df = loket.declarations.get_audit_trail(declaration_id="xxx-xxx")
        """
        try:
            # Get all pages automatically
            endpoint = f"providers/employers/employees/employments/declarations/{declaration_id}/audittrail"
            response_data = self.loket.get(
                endpoint=endpoint,
                filter_query=filter_query,
                order_by=order_by,
                get_all_pages=True
            )

            # Convert to DataFrame for validation
            if not response_data:
                # Return empty DataFrames if no data
                return pd.DataFrame(), pd.DataFrame()

            # Normalize nested JSON structure
            df = pd.json_normalize(response_data)

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, DeclarationAuditTrailGet)

            return valid_data, invalid_data

        except Exception as e:
            raise ValueError(f"Failed to get audit trail for declaration {declaration_id}: {e}") from e

    def get_by_employer(
        self,
        employer_id: str,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get a list of all declarations for all employments of a specific employer.

        Args:
            employer_id: The unique identifier of the employer
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated declaration data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            valid_df, invalid_df = loket.declarations.get_by_employer(employer_id="xxx-xxx")
        """
        try:
            # Get all pages automatically
            endpoint = f"providers/employers/{employer_id}/employees/employments/declarations"
            response_data = self.loket.get(
                endpoint=endpoint,
                filter_query=filter_query,
                order_by=order_by,
                get_all_pages=True
            )

            # Convert to DataFrame for validation
            if not response_data:
                # Return empty DataFrames if no data
                return pd.DataFrame(), pd.DataFrame()

            # Normalize nested JSON structure
            df = pd.json_normalize(response_data)

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, DeclarationGet)

            return valid_data, invalid_data

        except Exception as e:
            raise ValueError(f"Failed to get declarations for employer {employer_id}: {e}") from e

    def create(
        self,
        employment_id: str,
        data: Dict[str, Any],
    ) -> Response:
        """
        Create a new declaration for a specific employment using flat or nested payload input.

        Args:
            employment_id: The unique identifier of the employment
            data: Dictionary containing declaration data (flat or nested structure accepted)

        Returns:
            Response: API response from the create request

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the input data is invalid

        Example:
            # Flat data input
            data = {
                "payroll_component_key": 11,
                "calculated_distance_by_routing_service": 8,
                "number_of_units": 8,
                "declaration_date": "2017-11-01",
                "declaration_comment": "Overwerk project X",
                "reason_for_deviating_from_calculated_distance": "There were some ongoing road works i had to get around",
                "route_point_of_interest_name": "Van Spaendonck Groep",
                "route_address_freeform": "Reitseplein 1, 5037 AA Tilburg",
                "route_address_country_code": "NL",
                "route_position_latitude": 51.585996,
                "route_position_longitude": 5.585996
            }
            response = loket.declarations.create(employment_id="xxx-xxx", data=data)
        """
        try:
            # First, handle flat keys manually before flat_dict_to_nested_dict
            validated_data = DeclarationCreate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate declaration create data: {exc}") from exc

        response = self.loket.session.post(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/declarations",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response

    def update(self, declaration_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a declaration.

        Args:
            declaration_id: The ID of the declaration to update
            data: Dictionary containing the declaration data to update

        Returns:
            Dict containing the updated declaration data

        Raises:
            ValueError: If the declaration ID is invalid or data validation fails
            requests.exceptions.RequestException: If the API request fails

        Example:
            data = {
                "payroll_component_key": 11,
                "calculated_distance_by_routing_service": 8,
                "number_of_units": 8,
                "declaration_date": "2017-11-01",
                "declaration_comment": "Updated comment",
                "reason_for_deviating_from_calculated_distance": "Updated reason",
                "route_point_of_interest_name": "Updated Location",
                "route_address_freeform": "Updated Address",
                "route_address_country_code": "NL",
                "route_position_latitude": 51.585996,
                "route_position_longitude": 5.585996
            }
            response = loket.declarations.update(declaration_id="xxx-xxx", data=data)
        """
        if not declaration_id or not declaration_id.strip():
            raise ValueError("Declaration ID cannot be empty")

        try:
            # First, handle flat keys manually before flat_dict_to_nested_dict
            # Validate input data using Pydantic schema
            # The flat_to_nested validator on the schema will handle flat-to-nested conversion
            validated_data = DeclarationUpdate(**data)
            request_body = validated_data.model_dump(by_alias=True, mode="json", exclude_none=True)

        except Exception as exc:
            raise ValueError(f"Failed to validate declaration update data: {exc}") from exc

        response = self.loket.session.put(
            url=f"{self.loket.base_url}/providers/employers/employees/employments/declarations/{declaration_id}",
            json=request_body,
            timeout=self.loket.timeout,
        )

        response.raise_for_status()

        return response.json()

    def review(self, review_items: list) -> Dict[str, Any]:
        """
        Review (accept or reject) open declarations.

        Args:
            review_items: List of dictionaries containing declaration review data
                Each item should have 'id' and 'action' keys
                Example: [{"id": "xxx-xxx", "action": "accept"}]

        Returns:
            Dict containing the review response

        Raises:
            ValueError: If review_items is invalid or data validation fails
            requests.exceptions.RequestException: If the API request fails

        Example:
            review_items = [
                {"id": "b14acd0d-75d7-4fc8-8b22-4a3924585cab", "action": "accept"},
                {"id": "another-id", "action": "reject"}
            ]
            response = loket.declarations.review(review_items)
        """
        if not review_items or not isinstance(review_items, list):
            raise ValueError("Review items must be a non-empty list")

        try:
            # Validate each review item
            validated_items = []
            for item in review_items:
                validated_item = DeclarationReviewItem(**item)
                validated_items.append(validated_item.model_dump(by_alias=True, mode="json"))

            # Make the API request
            response: Response = self.loket.session.patch(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/declarations/review",
                json=validated_items,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()
            return response.json()

        except Exception as exc:
            raise ValueError(f"Failed to review declarations: {str(exc)}") from exc

    def process(self, process_items: list) -> Dict[str, Any]:
        """
        Process approved declarations.

        Args:
            process_items: List of dictionaries containing declaration process data
                Each item should have 'id' and 'payroll_period_id' keys
                Example: [{"id": "xxx-xxx", "payroll_period_id": 202004}]

        Returns:
            Dict containing the process response

        Raises:
            ValueError: If process_items is invalid or data validation fails
            requests.exceptions.RequestException: If the API request fails

        Example:
            process_items = [
                {"id": "b14acd0d-75d7-4fc8-8b22-4a3924585cab", "payroll_period_id": 202004},
                {"id": "another-id", "payroll_period_id": 202005}
            ]
            response = loket.declarations.process(process_items)
        """
        if not process_items or not isinstance(process_items, list):
            raise ValueError("Process items must be a non-empty list")

        try:
            # Validate each process item
            validated_items = []
            for item in process_items:
                validated_item = DeclarationProcessItem(**item)
                validated_items.append(validated_item.model_dump(by_alias=True, mode="json"))

            # Make the API request
            response: Response = self.loket.session.patch(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/declarations/process",
                json=validated_items,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()
            return response.json()

        except Exception as exc:
            raise ValueError(f"Failed to process declarations: {str(exc)}") from exc
