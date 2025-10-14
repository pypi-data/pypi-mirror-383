from pandera.typing import Series
import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class BenefitInKindTypesGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Benefit In Kind Types data returned from Loket API.
    A Benefit In Kind Type represents a type of benefit provided to employees.
    """
    # Main benefit in kind type fields
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the benefit in kind type", alias="id")
    description: Series[str] = pa.Field(coerce=True, description="Description of the benefit in kind type", alias="description")

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


# ==================== CREATE BENEFIT IN KIND TYPES SCHEMAS ====================

class BenefitInKindTypesCreate(BaseModel):
    """Schema for creating a benefit in kind type."""
    description: str = Field(..., description="The description of the benefit in kind type", example="Company Car", min_length=1, max_length=50)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class BenefitInKindTypesUpdate(BaseModel):
    """Schema for updating a benefit in kind type."""
    description: str = Field(..., description="The description of the benefit in kind type", example="Company Car", min_length=1, max_length=50)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"
