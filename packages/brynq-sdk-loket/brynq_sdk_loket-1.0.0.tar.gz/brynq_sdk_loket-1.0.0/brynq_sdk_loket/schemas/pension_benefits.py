from pandera.typing import Series
import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from brynq_sdk_functions import BrynQPanderaDataFrameModel


# ==================== PENSION BENEFITS SCHEMAS ====================

class PensionBenefitsGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Pension Benefits data returned from Loket API.
    Represents pension benefits associated with an employment.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the pension benefit", alias="id")
    start_date: Series[date] = pa.Field(coerce=True, description="Start date of the pension benefit", alias="startDate")
    end_date: Series[datetime] = pa.Field(coerce=True, description="End date of the pension benefit", alias="endDate", nullable=True)
    payout: Series[float] = pa.Field(coerce=True, description="Payout amount", alias="payout")

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


class PensionBenefitsCreate(BaseModel):
    """Schema for creating a pension benefit."""
    start_date: str = Field(..., alias="startDate", description="Start date of the pension benefit", example="2024-01-01")
    payout: float = Field(..., description="Payout amount", example=1000.00)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class PensionBenefitsUpdate(BaseModel):
    """Schema for updating a pension benefit."""
    start_date: Optional[str] = Field(None, alias="startDate", description="Start date of the pension benefit", example="2024-01-01")
    payout: Optional[float] = Field(None, description="Payout amount", example=1000.00)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"
