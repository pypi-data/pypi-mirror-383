from pandera.typing import Series
import pandera as pa
from pydantic import BaseModel, Field
from typing import Optional
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class CustomFieldsGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Custom Fields data returned from Loket API.
    Represents custom fields for an employer.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the custom field", alias="id")
    description: Series[str] = pa.Field(coerce=True, description="The description for the custom field", alias="description")

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


# ==================== CREATE CUSTOM FIELDS SCHEMAS ====================

class CustomFieldsCreate(BaseModel):
    """Schema for creating custom fields."""
    description: str = Field(..., max_length=50, description="The description for the custom field", example="Employee Level")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class CustomFieldsUpdate(BaseModel):
    """Schema for updating custom fields."""
    description: Optional[str] = Field(None, max_length=50, description="The description for the custom field", example="Employee Level")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"
