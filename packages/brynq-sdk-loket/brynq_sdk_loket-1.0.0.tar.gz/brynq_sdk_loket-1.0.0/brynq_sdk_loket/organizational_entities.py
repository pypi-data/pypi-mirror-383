"""
OrganizationalEntities resource class for Loket SDK.

This module provides methods for interacting with employment organizational entities-related endpoints
in the Loket API, including retrieving organizational entity information.
"""

from typing import Optional, Tuple, Dict, Any
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions as BrynQFunctions
from .schemas.organizational_entities import OrganizationalEntityGet, OrganizationalEntityCreate, OrganizationalEntityUpdate


class OrganizationalEntities:
    """
    Handles all organizational entities-related operations for Loket SDK.

    This class provides methods to interact with employment organizational entities endpoints,
    including retrieving organizational entity information.
    """

    def __init__(self, loket_instance):
        """
        Initialize the OrganizationalEntities resource.

        Args:
            loket_instance: The Loket client instance
        """
        self.loket = loket_instance

    def get(self, employment_id: Optional[str] = None, organizational_entity_id: Optional[str] = None, filter_query: Optional[str] = None, order_by: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get organizational entities data. Can retrieve either a list of organizational entities for an employment or a specific organizational entity by ID.

        Args:
            employment_id: The unique identifier of the employment (for getting all organizational entities)
            organizational_entity_id: The unique identifier of the organizational entity (for getting specific organizational entity)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)

        Example:
            # Get all organizational entities for an employment
            valid_df, invalid_df = loket.organizational_entities.get(employment_id="xxx-xxx")

            # Get specific organizational entity by ID
            valid_df, invalid_df = loket.organizational_entities.get(organizational_entity_id="yyy-yyy")
        """
        try:
            # Determine endpoint and parameters based on input
            if organizational_entity_id:
                if not organizational_entity_id.strip():
                    raise ValueError("Organizational entity ID cannot be empty")

                # Get specific organizational entity by ID
                endpoint = f"providers/employers/employees/employments/organizationalentities/{organizational_entity_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Extract content from response (get_by_id returns content object)
                if "content" in response_data:
                    organizational_entity_data = response_data["content"]
                else:
                    organizational_entity_data = response_data

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([organizational_entity_data])

            elif employment_id:
                # Get all organizational entities for employment
                endpoint = f"providers/employers/employees/employments/{employment_id}/organizationalentities"
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
                raise ValueError("Either employment_id or organizational_entity_id must be provided")

            valid_data, invalid_data = BrynQFunctions.validate_data(df, OrganizationalEntityGet)

            return valid_data, invalid_data

        except Exception as e:
            if organizational_entity_id:
                raise Exception(f"Failed to get organizational entity {organizational_entity_id}: {e}")
            else:
                raise Exception(f"Failed to get organizational entities for employment {employment_id}: {e}")

    def create(self, employment_id: str, data: Dict[str, Any]) -> Response:
        """
        Create a new organizational entity for an employment.

        Args:
            employment_id: The unique identifier of the employment
            data: Organizational entity data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the organizational entity data is invalid

        Example:
            # Create organizational entity with flat data structure
            response = loket.organizational_entities.create(
                employment_id="xxx-xxx",
                data={
                    "start_date": "2018-01-01",
                    "function_key": "b14acd0d-75d7-4fc8-8b22-4a3924585cab",
                    "deviating_function_group": "9A",
                    "deviating_function_description": "Directeur",
                    "standard_function_key": 1,
                    "department_key": "b14acd0d-75d7-4fc8-8b22-4a3924585cab",
                    "distribution_unit_key": "b14acd0d-75d7-4fc8-8b22-4a3924585cab",
                    "place_of_employment": "Amsterdam office",
                    "internal_telephone_extension_number": "678"
                }
            )
        """
        if not employment_id or not employment_id.strip():
            raise ValueError("Employment ID cannot be empty")

        try:
            # Validate and convert flat data to nested structure
            organizational_entity_data = OrganizationalEntityCreate(**data)
            request_body = organizational_entity_data.model_dump(by_alias=True, exclude_none=True)
            # Make POST request to create organizational entity
            response = self.loket.session.post(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/{employment_id}/organizationalentities",
                json=request_body,
                timeout=self.loket.timeout,
            )
            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to create organizational entity for employment {employment_id}: {e}")

    def update(self, organizational_entity_id: str, data: Dict[str, Any]) -> Response:
        """
        Update an existing organizational entity.

        Args:
            organizational_entity_id: The unique identifier of the organizational entity to update
            data: Organizational entity data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the organizational entity data is invalid

        Example:
            # Update organizational entity with flat data structure
            response = loket.organizational_entities.update(
                organizational_entity_id="xxx-xxx",
                data={
                    "start_date": "2018-01-01",
                    "function_key": "b14acd0d-75d7-4fc8-8b22-4a3924585cab",
                    "deviating_function_group": "9A",
                    "deviating_function_description": "Directeur",
                    "standard_function_key": 1,
                    "department_key": "b14acd0d-75d7-4fc8-8b22-4a3924585cab",
                    "distribution_unit_key": "b14acd0d-75d7-4fc8-8b22-4a3924585cab",
                    "place_of_employment": "Amsterdam office",
                    "internal_telephone_extension_number": "678"
                }
            )
        """
        try:
            # Validate and convert flat data to nested structure
            organizational_entity_data = OrganizationalEntityUpdate(**data)
            request_body = organizational_entity_data.model_dump(by_alias=True, exclude_none=True)
            # Make PUT request to update organizational entity
            response = self.loket.session.put(
                url=f"{self.loket.base_url}/providers/employers/employees/employments/organizationalentities/{organizational_entity_id}",
                json=request_body,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to update organizational entity {organizational_entity_id}: {e}")
