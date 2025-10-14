"""
Schema definitions for Contact-related data structures in Loket API.

This module contains Pandera schemas for GET operations and Pydantic schemas for CREATE/UPDATE operations
related to employee contacts.
"""

from typing import Optional, List, Dict, Any, Set
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field, model_validator

from brynq_sdk_functions import BrynQPanderaDataFrameModel, Functions
from ..utils import flat_to_nested_with_metadata
from .base import MetadataWithKey


# Prefix → target alias (nested object name)
PREFIX_MAP: Dict[str, str] = {
    "address": "address",
}

# Root level fields expecting MetadataWithKey (snake_case)
ROOT_METADATA_FIELDS: Set[str] = {
    # No root level metadata fields for contacts
}

# Nested level fields expecting MetadataWithKey (prefix → field set)
NESTED_METADATA_FIELDS: Dict[str, Set[str]] = {
    "address": {"country"},
}


class ContactAddress(BaseModel):
    """Schema for contact address information."""
    street: str = Field(..., description="Street name", example="Hoofdstraat")
    city: str = Field(..., description="City name", example="Amsterdam")
    house_number: int = Field(..., alias="houseNumber", description="House number", example=123)
    house_number_addition: Optional[str] = Field(None, alias="houseNumberAddition", description="House number addition", example="A")
    postal_code: str = Field(..., alias="postalCode", description="Postal code", example="1012AB")
    country: MetadataWithKey = Field(..., description="Country information")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"




class ContactCreate(BaseModel):
    """Schema for creating a contact."""
    name: str = Field(..., description="Full name of the contact person", example="Jan de Vries", max_length=100)
    description: str = Field(..., description="Relationship description (e.g., Moeder, Vader)", example="Moeder", max_length=50)
    phone_number: str = Field(..., alias="phoneNumber", description="Phone number of the contact", example="+31612345678", max_length=20)
    address: ContactAddress = Field(..., description="Address information")
    particularities: Optional[str] = Field(None, description="Additional notes or particularities about the contact", example="Emergency contact only", max_length=500)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"



    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using the generic function from brynq_sdk_functions.
        """
        return flat_to_nested_with_metadata(
            values=values,
            prefix_map=PREFIX_MAP,
            root_metadata_fields=ROOT_METADATA_FIELDS,
            nested_metadata_fields=NESTED_METADATA_FIELDS
        )


class ContactGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Contact data returned from Loket API.
    A Contact represents an emergency or reference contact for an employee.
    """
    # Main contact fields (flattened by pd.json_normalize from _embedded array)
    id: Series[str] = pa.Field(description="Unique identifier of the contact")
    name: Series[str] = pa.Field(description="Full name of the contact person")
    description: Series[str] = pa.Field(description="Relationship description (e.g., Moeder, Vader)")
    phone_number: Series[str] = pa.Field(alias="phoneNumber", description="Phone number of the contact")
    particularities: Series[str] = pa.Field(description="Additional notes or particularities about the contact")

    # Address fields (nested structure flattened by pd.json_normalize)
    address_street: Series[str] = pa.Field(alias="address.street", description="Street name")
    address_city: Series[str] = pa.Field(alias="address.city", description="City name")
    address_house_number: Series[int] = pa.Field(alias="address.houseNumber", description="House number")
    address_house_number_addition: Series[str] = pa.Field(alias="address.houseNumberAddition", description="House number addition", nullable=True)
    address_postal_code: Series[str] = pa.Field(alias="address.postalCode", description="Postal code")
    address_country_key: Series[int] = pa.Field(alias="address.country.key", description="Country key")
    address_country_value: Series[str] = pa.Field(alias="address.country.value", description="Country name")
    address_country_iso_code: Series[str] = pa.Field(alias="address.country.isoCode", description="Country ISO code")

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
