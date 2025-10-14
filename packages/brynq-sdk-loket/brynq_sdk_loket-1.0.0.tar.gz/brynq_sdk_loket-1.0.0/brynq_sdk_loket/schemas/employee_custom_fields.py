from pandera.typing import Series
import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class EmployeeCustomFieldsGet(BrynQPanderaDataFrameModel):
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the employee custom field", alias="id")
    custom_field_id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the custom field as defined at the employer level", alias="customField.id")
    custom_field_description: Series[str] = pa.Field(coerce=True, description="The description for the custom field", alias="customField.description", nullable=True)
    value: Series[str] = pa.Field(coerce=True, description="The value for the custom field for the employee", alias="value", nullable=True)
    custom_field: Series[str] = pa.Field(coerce=True, description="The custom field object", alias="customField", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


class CustomFieldCreate(BaseModel):
    id: str = Field(..., description="The unique identifier of the custom field")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class EmployeeCustomFieldsCreate(BaseModel):
    custom_field: CustomFieldCreate = Field(..., alias="customField", description="The custom field")
    value: str = Field(..., description="The value for the custom field for the employee", example="Senior Developer")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class EmployeeCustomFieldsUpdate(BaseModel):
    value: str = Field(..., description="The value for the custom field for the employee", example="Senior Developer")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"
