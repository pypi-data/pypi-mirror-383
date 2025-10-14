from pandera.typing import Series
import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any, Set
from datetime import date
from brynq_sdk_functions import BrynQPanderaDataFrameModel, Functions
from ..utils import flat_to_nested_with_metadata
from .base import MetadataWithKey
from datetime import date, datetime


# ==================== SOCIAL SECURITY BENEFITS SCHEMAS ====================

class SocialSecurityBenefitsGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Social Security Benefits data returned from Loket API.
    Represents social security benefits associated with an employment.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the social security benefit", alias="id")
    start_date: Series[date] = pa.Field(coerce=True, description="Start date of the social security benefit", alias="startDate")
    end_date: Series[date] = pa.Field(coerce=True, description="End date of the social security benefit", alias="endDate", nullable=True)

    # Supplementation
    supplementation_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The key of the supplementation type", alias="supplementation.type.key", nullable=True)
    supplementation_type_value: Series[str] = pa.Field(coerce=True, description="Value of the supplementation type", alias="supplementation.type.value", nullable=True)
    supplementation_percentage: Series[float] = pa.Field(coerce=True, description="Percentage of supplementation", alias="supplementation.percentage", nullable=True)

    # Benefit
    benefit_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The key of the benefit type", alias="benefit.type.key", nullable=True)
    benefit_type_value: Series[str] = pa.Field(coerce=True, description="Value of the benefit type", alias="benefit.type.value", nullable=True)
    benefit_percentage: Series[float] = pa.Field(coerce=True, description="Percentage of benefit", alias="benefit.percentage", nullable=True)

    # Fields that may come as full objects (not normalized by pd.json_normalize)
    supplementation: Series[str] = pa.Field(coerce=True, description="Supplementation object", alias="supplementation", nullable=True)
    benefit: Series[str] = pa.Field(coerce=True, description="Benefit object", alias="benefit", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


class SupplementationData(BaseModel):
    """Supplementation data for social security benefits."""
    type: Optional[MetadataWithKey] = Field(None, description="Type of supplementation")
    percentage: Optional[float] = Field(None, description="Percentage of supplementation")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class BenefitData(BaseModel):
    """Benefit data for social security benefits."""
    type: Optional[MetadataWithKey] = Field(None, description="Type of benefit")
    percentage: Optional[float] = Field(None, description="Percentage of benefit")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class SocialSecurityBenefitsCreate(BaseModel):
    """Schema for creating a social security benefit."""
    start_date: str = Field(..., alias="startDate", description="Start date of the social security benefit", example="2024-01-01")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the social security benefit", example="2024-12-31")
    supplementation: Optional[SupplementationData] = Field(None, description="Supplementation information")
    benefit: Optional[BenefitData] = Field(None, description="Benefit information")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using shared helper.
        Supports supplementation_* and benefit_* prefixed fields.
        """
        if not isinstance(values, dict):
            return values

        # If already properly nested, return as is
        if "supplementation" in values and isinstance(values["supplementation"], dict):
            return values

        prefix_map: Dict[str, str] = {
            "supplementation": "supplementation",
            "benefit": "benefit",
        }

        nested_metadata_fields: Dict[str, Set[str]] = {
            "supplementation": {"type"},
            "benefit": {"type"},
        }

        return flat_to_nested_with_metadata(
            values=values,
            prefix_map=prefix_map,
            root_metadata_fields=set(),
            nested_metadata_fields=nested_metadata_fields
        )


class SocialSecurityBenefitsUpdate(BaseModel):
    """Schema for updating a social security benefit."""
    start_date: Optional[str] = Field(None, alias="startDate", description="Start date of the social security benefit", example="2024-01-01")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the social security benefit", example="2024-12-31")
    supplementation: Optional[SupplementationData] = Field(None, description="Supplementation information")
    benefit: Optional[BenefitData] = Field(None, description="Benefit information")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(values, dict):
            return values

        # If already properly nested, return as is
        if "supplementation" in values and isinstance(values["supplementation"], dict):
            return values

        prefix_map: Dict[str, str] = {
            "supplementation": "supplementation",
            "benefit": "benefit",
        }

        nested_metadata_fields: Dict[str, Set[str]] = {
            "supplementation": {"type"},
            "benefit": {"type"},
        }

        return flat_to_nested_with_metadata(
            values=values,
            prefix_map=prefix_map,
            root_metadata_fields=set(),
            nested_metadata_fields=nested_metadata_fields
        )
