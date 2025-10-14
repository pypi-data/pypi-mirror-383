"""
Contact resource class for Loket SDK.

This module provides methods for interacting with employee contact-related endpoints
in the Loket API, including retrieving contact information.
"""

from typing import Optional, Tuple, Dict, Any
import pandas as pd
from requests import Response

from brynq_sdk_functions import Functions
from .schemas.contacts import ContactGet, ContactCreate


class Contacts:
    """
    Handles all contact-related operations for Loket SDK.

    This class provides methods to interact with employee contact endpoints,
    including retrieving contact information for employees.
    """

    def __init__(self, loket_instance):
        """
        Initialize the Contacts resource.

        Args:
            loket_instance: The Loket client instance
        """
        self.loket = loket_instance

    def get(self, employee_id: Optional[str] = None, contact_id: Optional[str] = None, filter_query: Optional[str] = None, order_by: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get contacts data. Can retrieve either a list of contacts for an employee or a specific contact by ID.

        Args:
            employee_id: The unique identifier of the employee (for getting all contacts)
            contact_id: The unique identifier of the contact (for getting specific contact)
            filter_query: Filter the collection (OData-style filter)
            order_by: Order the collection on one or more fields

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Tuple of (valid_data, invalid_data)
                - valid_data: DataFrame containing validated contact data
                - invalid_data: DataFrame containing data that failed validation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response data is invalid

        Example:
            # Get all contacts for an employee
            valid_df, invalid_df = loket.contacts.get(employee_id="xxx-xxx")

            # Get specific contact by ID
            valid_df, invalid_df = loket.contacts.get(contact_id="yyy-yyy")

            # Get contacts with filter (phone number not null)
            valid_df, invalid_df = loket.contacts.get(employee_id="xxx-xxx", filter_query="phoneNumber ne null")
        """
        try:
            # Determine endpoint and parameters based on input
            if contact_id:
                if not contact_id.strip():
                    raise ValueError("Contact ID cannot be empty")

                # Get specific contact by ID
                endpoint = f"providers/employers/employees/contacts/{contact_id}"
                response_data = self.loket.get(
                    endpoint=endpoint,
                    get_all_pages=False
                )

                # Convert to DataFrame for validation
                if not response_data:
                    return pd.DataFrame(), pd.DataFrame()

                # Extract content from response (get_by_id returns content object)
                if "content" in response_data:
                    contact_data = response_data["content"]
                else:
                    contact_data = response_data

                # Normalize nested JSON structure (single item in list)
                df = pd.json_normalize([contact_data])

            elif employee_id:
                # Get all contacts for employee
                endpoint = f"providers/employers/employees/{employee_id}/contacts"
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
                raise ValueError("Either employee_id or contact_id must be provided")

            # Validate data using Pandera schema
            valid_data, invalid_data = Functions.validate_data(df, ContactGet)

            return valid_data, invalid_data

        except Exception as e:
            if contact_id:
                raise ValueError(f"Failed to get contact {contact_id}: {e}") from e
            else:
                raise ValueError(f"Failed to get contacts for employee {employee_id}: {e}") from e

    def create(self, employee_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new contact for an employee.

        Args:
            employee_id: The unique identifier of the employee
            data: Dictionary containing the contact data

        Returns:
            Dict containing the created contact data

        Raises:
            ValueError: If the employee ID is invalid or data validation fails
            requests.exceptions.RequestException: If the API request fails

        Example:
            data = {
                "name": "Johanna Bakker",
                "description": "Moeder",
                "phone_number": "013-12345678",
                "address_street": "Voordijk",
                "address_city": "Leiden",
                "address_house_number": 12,
                "address_house_number_addition": "D",
                "address_postal_code": "1234 AA",
                "address_country_key": 1,
                "particularities": "Genoemd adres is een priveadres"
            }
            response = loket.contacts.create(employee_id="xxx-xxx", data=data)
        """
        if not employee_id or not employee_id.strip():
            raise ValueError("Employee ID cannot be empty")

        try:
            # Validate and convert flat data to nested structure
            contact_data = ContactCreate(**data)
            request_body = contact_data.model_dump(by_alias=True, exclude_none=True)

            # Make POST request to create contact
            response = self.loket.session.post(
                url=f"{self.loket.base_url}/providers/employers/employees/{employee_id}/contacts",
                json=request_body,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to create contact for employee {employee_id}: {e}")

    def update(self, contact_id: str, **kwargs) -> Response:
        """
        Update an existing contact.

        Args:
            contact_id: The unique identifier of the contact to update
            **kwargs: Contact data fields (flat structure will be converted to nested)

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the contact data is invalid

        Example:
            # Update contact with flat data structure
            response = loket.contacts.update(
                contact_id="xxx-xxx",
                name="Johanna Bakker",
                description="Moeder",
                phone_number="013-12345678",
                address_street="Voordijk",
                address_city="Leiden",
                address_house_number=12,
                address_house_number_addition="D",
                address_postal_code="1234 AA",
                address_country_key=1,
                particularities="Genoemd adres is een priveadres"
            )
        """
        try:
            # Validate and convert flat data to nested structure
            contact_data = ContactCreate(**kwargs)
            request_body = contact_data.model_dump(by_alias=True, exclude_none=True)

            # Make PUT request to update contact
            response = self.loket.session.put(
                url=f"{self.loket.base_url}/providers/employers/employees/contacts/{contact_id}",
                json=request_body,
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to update contact {contact_id}: {e}")

    def delete(self, contact_id: str) -> Response:
        """
        Delete an existing contact.

        Args:
            contact_id: The unique identifier of the contact to delete

        Returns:
            Response: The HTTP response from the API

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the contact_id is invalid

        Example:
            # Delete a contact
            response = loket.contacts.delete(contact_id="xxx-xxx")
        """
        try:
            if not contact_id or not contact_id.strip():
                raise ValueError("Contact ID cannot be empty")

            # Make DELETE request to delete contact
            response = self.loket.session.delete(
                url=f"{self.loket.base_url}/providers/employers/employees/contacts/{contact_id}",
                timeout=self.loket.timeout,
            )

            response.raise_for_status()

            return response

        except Exception as e:
            raise Exception(f"Failed to delete contact {contact_id}: {e}")
