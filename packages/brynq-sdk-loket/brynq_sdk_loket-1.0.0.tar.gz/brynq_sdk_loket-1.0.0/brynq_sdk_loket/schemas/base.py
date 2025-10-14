"""
Base schemas for common metadata objects used across Loket SDK.

This module contains shared metadata schemas that are used by multiple
entity schemas (employees, employers, employments, etc.).
"""

from pydantic import BaseModel, Field
from typing import Optional


class MetadataWithKey(BaseModel):
    """
    Base metadata schema with only key field (mandatory).

    This is the most basic metadata object where only the key is required.
    The API accepts just the key and can provide the value automatically.
    """
    key: int = Field(..., description="The key identifier for the metadata")


class MetadataWithStringKey(BaseModel):
    """
    Base metadata schema with string key field (mandatory).

    Used for cases where the key is a string (like department IDs).
    """
    key: str = Field(..., description="The string key identifier for the metadata")


class MetadataWithKeyAndValue(BaseModel):
    """
    Metadata schema with key (mandatory) and value (optional).

    While the value can be provided, it's optional since the API
    can determine the value from the key.
    """
    key: int = Field(..., description="The key identifier for the metadata")
    value: Optional[str] = Field(None, description="The value description for the metadata")


class MetadataWithKeyAndIsoCode(BaseModel):
    """
    Country metadata schema with key (mandatory), value (optional) and ISO code (optional).

    Used specifically for country metadata where ISO code might be needed.
    """
    key: int = Field(..., description="The key identifier for the country")
    value: Optional[str] = Field(None, description="The value description for the country")
    iso_code: Optional[str] = Field(None, alias="isoCode", description="The ISO 3166-1 alpha-2 value for the country", max_length=2)


class CountryWithIsoCode(BaseModel):
    """
    Country metadata with ISO code support.

    Extended country metadata that includes ISO code field.
    """
    iso_code: Optional[str] = Field(None, alias="isoCode", description="The ISO 3166-1 alpha-2 value for the country", max_length=2)
    key: int = Field(..., description="The key identifier for the country")
    value: Optional[str] = Field(None, description="The value description for the country")


# Legacy alias for backward compatibility
MetadataObject = MetadataWithKeyAndValue
