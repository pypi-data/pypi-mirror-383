"""
Schema definitions for Children-related data structures in Loket API.

This module contains Pandera schemas for GET operations and Pydantic schemas for CREATE/UPDATE operations
related to employee children.
"""

from typing import Optional, Dict, Any, Set
import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field, model_validator

from brynq_sdk_functions import BrynQPanderaDataFrameModel, Functions
from ..utils import flat_to_nested_with_metadata
from .base import MetadataWithKey


class ChildGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Child data returned from Loket API.
    A Child represents a child of an employee in the Loket system.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the child", alias="id")
    first_name: Series[str] = pa.Field(coerce=True, description="The first name of the child", alias="firstName")
    last_name: Series[str] = pa.Field(coerce=True, description="The last name of the child", alias="lastName")
    prefix: Series[str] = pa.Field(coerce=True, description="The prefix of the child", alias="prefix", nullable=True)
    initials: Series[str] = pa.Field(coerce=True, description="The initials of the child", alias="initials", nullable=True)
    date_of_birth: Series[str] = pa.Field(coerce=True, description="The date of birth of the child", alias="dateOfBirth")
    date_of_death: Series[str] = pa.Field(coerce=True, description="The date of death of the child", alias="dateOfDeath", nullable=True)
    gender_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Gender key", alias="gender.key", nullable=True)
    gender_value: Series[str] = pa.Field(coerce=True, description="Gender value", alias="gender.value", nullable=True)
    residence_status_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Residence status key", alias="residenceStatus.key", nullable=True)
    residence_status_value: Series[str] = pa.Field(coerce=True, description="Residence status value", alias="residenceStatus.value", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False


# Prefix → target alias (nested object name)
PREFIX_MAP: Dict[str, str] = {
    # No prefixes for children, only root level metadata fields
}

# Root level fields expecting MetadataWithKey (snake_case)
ROOT_METADATA_FIELDS: Set[str] = {
    "gender",
    "residence_status",
}

# Nested level fields expecting MetadataWithKey (prefix → field set)
NESTED_METADATA_FIELDS: Dict[str, Set[str]] = {
    # No nested metadata fields for children
}


class ChildCreate(BaseModel):
    """Schema for creating/updating a child."""
    first_name: str = Field(..., alias="firstName", description="First name of the child", example="Emma", max_length=100)
    last_name: str = Field(..., alias="lastName", description="Last name of the child", example="Smith", max_length=100)
    prefix: Optional[str] = Field(None, description="Prefix of the child", example="van", max_length=20)
    initials: Optional[str] = Field(None, description="Initials of the child", example="E.", max_length=10)
    date_of_birth: str = Field(..., alias="dateOfBirth", description="Date of birth of the child (YYYY-MM-DD)", example="2015-03-20")
    date_of_death: Optional[str] = Field(None, alias="dateOfDeath", description="Date of death of the child (YYYY-MM-DD)", example="2024-01-15")
    gender: MetadataWithKey = Field(..., description="Gender information")
    residence_status: MetadataWithKey = Field(..., alias="residenceStatus", description="Residence status information")

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
