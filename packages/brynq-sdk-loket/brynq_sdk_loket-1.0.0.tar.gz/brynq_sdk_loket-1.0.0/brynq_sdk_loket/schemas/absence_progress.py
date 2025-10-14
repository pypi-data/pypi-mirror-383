from pandera.typing import Series
import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from .base import MetadataWithKey


class AbsenceProgressGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Absence Progress data returned from Loket API.
    An Absence Progress represents the progress tracking of an absence period.
    """
    # Main progress fields
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the absence progress", alias="id")
    start_date: Series[str] = pa.Field(coerce=True, description="Start date of the progress period", alias="startDate")
    end_date: Series[str] = pa.Field(coerce=True, description="End date of the progress period", alias="endDate", nullable=True)
    incapacity_percentage: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Percentage of incapacity during this period", alias="incapacityPercentage", nullable=True)

    # Type of work resumption
    type_of_work_resumption_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The key of the type of work resumption", alias="typeOfWorkResumption.key", nullable=True)
    type_of_work_resumption_value: Series[str] = pa.Field(coerce=True, description="Description of the type of work resumption", alias="typeOfWorkResumption.value", nullable=True)

    # Comments
    comments: Series[str] = pa.Field(coerce=True, description="Free text field for relevant information", alias="comments", nullable=True)

    # Fields that may come as full objects (not normalized by pd.json_normalize)
    type_of_work_resumption: Series[str] = pa.Field(coerce=True, description="Type of work resumption object", alias="typeOfWorkResumption", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


# ==================== CREATE ABSENCE PROGRESS SCHEMAS ====================

class AbsenceProgressCreate(BaseModel):
    """Schema for creating an absence progress."""
    start_date: str = Field(..., alias="startDate", description="Start date of the progress period", example="2024-01-01")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the progress period", example="2024-01-31")
    incapacity_percentage: int = Field(..., alias="incapacityPercentage", description="Percentage of incapacity during this period", example=50, ge=0, le=100)
    type_of_work_resumption: Optional[MetadataWithKey] = Field(None, alias="typeOfWorkResumption", description="Type of work resumption")
    comments: Optional[str] = Field(None, description="Free text field for relevant information", example="Gradual return to work", max_length=4000)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class AbsenceProgressUpdate(BaseModel):
    """Schema for updating an absence progress."""
    start_date: Optional[str] = Field(None, alias="startDate", description="Start date of the progress period", example="2024-01-01")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the progress period", example="2024-01-31")
    incapacity_percentage: Optional[int] = Field(None, alias="incapacityPercentage", description="Percentage of incapacity during this period", example=50, ge=0, le=100)
    type_of_work_resumption: Optional[MetadataWithKey] = Field(None, alias="typeOfWorkResumption", description="Type of work resumption")
    comments: Optional[str] = Field(None, description="Free text field for relevant information", example="Gradual return to work", max_length=4000)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"
