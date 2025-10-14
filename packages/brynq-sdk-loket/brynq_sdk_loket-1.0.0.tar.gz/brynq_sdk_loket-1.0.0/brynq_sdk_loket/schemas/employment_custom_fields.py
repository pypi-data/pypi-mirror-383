from pandera.typing import Series
import pandera as pa
from pydantic import BaseModel, Field
from typing import Optional
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class EmploymentCustomFieldsGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Employment Custom Fields data returned from Loket API.
    Represents custom field values for an employment.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the employment custom field", alias="id")
    value: Series[str] = pa.Field(coerce=True, description="The value for the custom field for the employment", alias="value")

    # Custom field metadata fields
    custom_field_id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the custom field", alias="customField.id")
    custom_field_description: Series[str] = pa.Field(coerce=True, description="The description of the custom field", alias="customField.description")

    # Fields that may come as full objects (not normalized by pd.json_normalize)
    custom_field: Series[str] = pa.Field(coerce=True, description="Custom field object", alias="customField", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


# ==================== CREATE EMPLOYMENT CUSTOM FIELDS SCHEMAS ====================

class CustomFieldMetadata(BaseModel):
    """Custom field metadata for creating employment custom fields."""
    id: str = Field(..., description="The unique identifier of the custom field")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class EmploymentCustomFieldsCreate(BaseModel):
    """Schema for creating employment custom fields."""
    custom_field: CustomFieldMetadata = Field(..., alias="customField", description="The custom field metadata")
    value: str = Field(..., max_length=255, description="The value for the custom field for the employment", example="Full-time")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class EmploymentCustomFieldsUpdate(BaseModel):
    """Schema for updating employment custom fields."""
    value: Optional[str] = Field(None, max_length=255, description="The value for the custom field for the employment", example="Full-time")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"
