"""
Schema definitions for Partners-related data structures in Loket API.

This module contains Pandera schemas for GET operations and Pydantic schemas for CREATE/UPDATE operations
related to employee partners.
"""

from typing import Optional, Dict, Any, Set
import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field, model_validator

from brynq_sdk_functions import BrynQPanderaDataFrameModel, Functions
from ..utils import flat_to_nested_with_metadata
from .base import MetadataWithKey


class PartnerGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Partner data returned from Loket API.
    A Partner represents a partner of an employee in the Loket system.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the partner", alias="id")
    start_date: Series[str] = pa.Field(coerce=True, description="The start date of the partnership", alias="startDate")
    end_date: Series[str] = pa.Field(coerce=True, description="The end date of the partnership", alias="endDate", nullable=True)
    first_name: Series[str] = pa.Field(coerce=True, description="The first name of the partner", alias="firstName")
    last_name: Series[str] = pa.Field(coerce=True, description="The last name of the partner", alias="lastName")
    prefix: Series[str] = pa.Field(coerce=True, description="The prefix of the partner", alias="prefix", nullable=True)
    initials: Series[str] = pa.Field(coerce=True, description="The initials of the partner", alias="initials", nullable=True)
    date_of_birth: Series[str] = pa.Field(coerce=True, description="The date of birth of the partner", alias="dateOfBirth")
    place_of_birth: Series[str] = pa.Field(coerce=True, description="The place of birth of the partner", alias="placeOfBirth", nullable=True)
    date_of_death: Series[str] = pa.Field(coerce=True, description="The date of death of the partner", alias="dateOfDeath", nullable=True)
    how_to_format_last_name_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="How to format last name key", alias="howToFormatLastName.key", nullable=True)
    how_to_format_last_name_value: Series[str] = pa.Field(coerce=True, description="How to format last name value", alias="howToFormatLastName.value", nullable=True)
    title_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Title key", alias="title.key", nullable=True)
    title_value: Series[str] = pa.Field(coerce=True, description="Title value", alias="title.value", nullable=True)
    gender_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Gender key", alias="gender.key", nullable=True)
    gender_value: Series[str] = pa.Field(coerce=True, description="Gender value", alias="gender.value", nullable=True)
    wao_classification_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="WAO classification key", alias="waoClassification.key", nullable=True)
    wao_classification_value: Series[str] = pa.Field(coerce=True, description="WAO classification value", alias="waoClassification.value", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False


class PartnerCreate(BaseModel):
    """Schema for creating/updating a partner."""
    start_date: str = Field(..., alias="startDate", description="Start date of the partnership (YYYY-MM-DD)", example="2024-01-01")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the partnership (YYYY-MM-DD)", example="2024-12-31")
    first_name: str = Field(..., alias="firstName", description="First name of the partner", example="Jane", max_length=100)
    last_name: str = Field(..., alias="lastName", description="Last name of the partner", example="Doe", max_length=100)
    prefix: Optional[str] = Field(None, description="Prefix of the partner", example="van", max_length=20)
    initials: Optional[str] = Field(None, description="Initials of the partner", example="J.", max_length=10)
    date_of_birth: str = Field(..., alias="dateOfBirth", description="Date of birth of the partner (YYYY-MM-DD)", example="1990-05-15")
    place_of_birth: Optional[str] = Field(None, alias="placeOfBirth", description="Place of birth of the partner", example="Amsterdam", max_length=100)
    date_of_death: Optional[str] = Field(None, alias="dateOfDeath", description="Date of death of the partner (YYYY-MM-DD)")
    how_to_format_last_name: MetadataWithKey = Field(..., alias="howToFormatLastName", description="How to format last name information")
    title: MetadataWithKey = Field(..., description="Title information")
    gender: MetadataWithKey = Field(..., description="Gender information")
    wao_classification: MetadataWithKey = Field(..., alias="waoClassification", description="WAO classification information")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using shared helper.
        Supports *_key fields for metadata objects (how_to_format_last_name, title, gender, wao_classification).
        """
        if not isinstance(values, dict):
            return values

        root_metadata_fields: Set[str] = {
            "how_to_format_last_name",
            "title",
            "gender",
            "wao_classification",
        }

        return flat_to_nested_with_metadata(
            values=values,
            prefix_map={},
            root_metadata_fields=root_metadata_fields,
            nested_metadata_fields={}
        )
