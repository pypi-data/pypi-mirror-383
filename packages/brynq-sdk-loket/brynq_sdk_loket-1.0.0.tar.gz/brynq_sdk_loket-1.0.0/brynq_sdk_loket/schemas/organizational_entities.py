"""
Schema definitions for OrganizationalEntities-related data structures in Loket API.

This module contains Pandera schemas for GET operations related to employment organizational entities.
"""

from typing import Optional, Dict, Any, Set
import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field, model_validator

from brynq_sdk_functions import BrynQPanderaDataFrameModel, Functions
from ..utils import flat_to_nested_with_metadata
from .base import MetadataWithKey, MetadataWithStringKey


class OrganizationalEntityGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating OrganizationalEntity data returned from Loket API.
    An OrganizationalEntity represents organizational assignment information for an employment in the Loket system.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the organizational entity", alias="id")
    start_date: Series[str] = pa.Field(coerce=True, description="The start date of the organizational entity", alias="startDate")
    end_date: Series[str] = pa.Field(coerce=True, description="The end date of the organizational entity", alias="endDate", nullable=True)

    # Function fields
    function_key: Series[str] = pa.Field(coerce=True, description="Function key", alias="function.key", nullable=True)
    function_description: Series[str] = pa.Field(coerce=True, description="Function description", alias="function.description", nullable=True)
    function_group: Series[str] = pa.Field(coerce=True, description="Function group", alias="function.group", nullable=True)

    # Deviating function fields
    deviating_function_group: Series[str] = pa.Field(coerce=True, description="Deviating function group", alias="deviatingFunctionGroup", nullable=True)
    deviating_function_description: Series[str] = pa.Field(coerce=True, description="Deviating function description", alias="deviatingFunctionDescription", nullable=True)

    # Standard function fields (optional - only when standardFunction is not null)
    standard_function_key: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, description="Standard function key", alias="standardFunction.key", nullable=True)
    standard_function_value: Optional[Series[str]] = pa.Field(coerce=True, description="Standard function value", alias="standardFunction.value", nullable=True)
    standard_function_code: Optional[Series[str]] = pa.Field(coerce=True, description="Standard function code", alias="standardFunction.code", nullable=True)
    standard_function_category: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, description="Standard function category", alias="standardFunction.category", nullable=True)

    # Department fields
    department_key: Series[str] = pa.Field(coerce=True, description="Department key", alias="department.key", nullable=True)
    department_code: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Department code", alias="department.code", nullable=True)
    department_description: Series[str] = pa.Field(coerce=True, description="Department description", alias="department.description", nullable=True)

    # Distribution unit fields
    distribution_unit_key: Series[str] = pa.Field(coerce=True, description="Distribution unit key", alias="distributionUnit.key", nullable=True)
    distribution_unit_code: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Distribution unit code", alias="distributionUnit.code", nullable=True)
    distribution_unit_description: Series[str] = pa.Field(coerce=True, description="Distribution unit description", alias="distributionUnit.description", nullable=True)

    # Additional fields
    place_of_employment: Series[str] = pa.Field(coerce=True, description="Place of employment", alias="placeOfEmployment", nullable=True)
    internal_telephone_extension_number: Series[str] = pa.Field(coerce=True, description="Internal telephone extension number", alias="internalTelephoneExtensionNumber", nullable=True)

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "function_key": {
                "parent_schema": "FunctionGet",
                "parent_column": "key",
                "cardinality": "N:1"
            },
            "department_key": {
                "parent_schema": "DepartmentGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

    class Config:
        coerce = True
        strict = False


class OrganizationalEntityCreate(BaseModel):
    """Schema for creating an organizational entity."""
    start_date: str = Field(..., alias="startDate", description="Start date of the organizational entity (YYYY-MM-DD)", example="2024-01-01")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the organizational entity (YYYY-MM-DD)", example="2024-12-31")
    function: Optional[MetadataWithStringKey] = Field(None, description="Function information")
    deviating_function_group: Optional[str] = Field(None, alias="deviatingFunctionGroup", description="Deviating function group", example="IT")
    deviating_function_description: Optional[str] = Field(None, alias="deviatingFunctionDescription", description="Deviating function description", example="Senior Developer")
    standard_function: Optional[MetadataWithKey] = Field(None, alias="standardFunction", description="Standard function information")
    department: Optional[MetadataWithStringKey] = Field(None, description="Department information")
    distribution_unit: Optional[MetadataWithStringKey] = Field(None, alias="distributionUnit", description="Distribution unit information")
    place_of_employment: Optional[str] = Field(None, alias="placeOfEmployment", description="Place of employment", example="Amsterdam Office")
    internal_telephone_extension_number: Optional[str] = Field(None, alias="internalTelephoneExtensionNumber", description="Internal telephone extension number")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using shared helper.
        Supports *_key fields for metadata objects (function, standard_function, department, distribution_unit).
        """
        if not isinstance(values, dict):
            return values

        root_metadata_fields: Set[str] = {"function", "standard_function", "department", "distribution_unit"}

        return flat_to_nested_with_metadata(
            values=values,
            prefix_map={},
            root_metadata_fields=root_metadata_fields,
            nested_metadata_fields={}
        )


class OrganizationalEntityUpdate(BaseModel):
    """Schema for updating an organizational entity."""
    start_date: str = Field(..., alias="startDate", description="Start date of the organizational entity (YYYY-MM-DD)", example="2024-01-01")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the organizational entity (YYYY-MM-DD)", example="2024-12-31")
    function: Optional[MetadataWithStringKey] = Field(None, description="Function information")
    deviating_function_group: Optional[str] = Field(None, alias="deviatingFunctionGroup", description="Deviating function group", example="IT")
    deviating_function_description: Optional[str] = Field(None, alias="deviatingFunctionDescription", description="Deviating function description", example="Senior Developer")
    standard_function: Optional[MetadataWithKey] = Field(None, alias="standardFunction", description="Standard function information")
    department: Optional[MetadataWithStringKey] = Field(None, description="Department information")
    distribution_unit: Optional[MetadataWithStringKey] = Field(None, alias="distributionUnit", description="Distribution unit information")
    place_of_employment: Optional[str] = Field(None, alias="placeOfEmployment", description="Place of employment", example="Amsterdam Office")
    internal_telephone_extension_number: Optional[str] = Field(None, alias="internalTelephoneExtensionNumber", description="Internal telephone extension number")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(values, dict):
            return values

        root_metadata_fields: Set[str] = {"function", "standard_function", "department", "distribution_unit"}

        return flat_to_nested_with_metadata(
            values=values,
            prefix_map={},
            root_metadata_fields=root_metadata_fields,
            nested_metadata_fields={}
        )
