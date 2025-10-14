from pandera.typing import Series
import pandera as pa
from pydantic import BaseModel, Field
from typing import Optional
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class BenefitsInKindGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Benefits In Kind data returned from Loket API.
    Represents benefits in kind associated with an employment.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the benefits in kind", alias="id")
    start_date: Series[str] = pa.Field(coerce=True, description="Start date of the benefits in kind", alias="startDate")
    end_date: Series[str] = pa.Field(coerce=True, description="End date of the benefits in kind", alias="endDate", nullable=True)
    brand: Series[str] = pa.Field(coerce=True, description="Brand of the benefit", alias="brand", nullable=True)
    type: Series[str] = pa.Field(coerce=True, description="Type of the benefit", alias="type", nullable=True)
    value: Series[float] = pa.Field(coerce=True, description="Value of the benefit", alias="value")
    supplier: Series[str] = pa.Field(coerce=True, description="Supplier of the benefit", alias="supplier", nullable=True)
    particularities: Series[str] = pa.Field(coerce=True, description="Particularities of the benefit", alias="particularities", nullable=True)

    # Benefit in kind type fields
    benefit_inkind_type_id: Series[str] = pa.Field(coerce=True, description="The ID of the benefit in kind type", alias="benefitInKindType.id", nullable=True)
    benefit_inkind_type_description: Series[str] = pa.Field(coerce=True, description="Description of the benefit in kind type", alias="benefitInKindType.description", nullable=True)

    # Fields that may come as full objects (not normalized by pd.json_normalize)
    benefit_inkind_type: Series[str] = pa.Field(coerce=True, description="Benefit in kind type object", alias="benefitInKindType", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


# ==================== CREATE BENEFITS IN KIND SCHEMAS ====================

class BenefitInKindTypeCreate(BaseModel):
    """Benefit in kind type for creating benefits in kind."""
    id: str = Field(..., description="The ID of the benefit in kind type")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class BenefitsInKindCreate(BaseModel):
    """Schema for creating benefits in kind."""
    start_date: str = Field(..., alias="startDate", description="Start date of the benefits in kind", example="2024-01-01")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the benefits in kind", example="2024-12-31")
    benefit_inkind_type: BenefitInKindTypeCreate = Field(..., alias="benefitInKindType", description="Benefit in kind type")
    brand: Optional[str] = Field(None, description="Brand of the benefit", example="Apple")
    type: Optional[str] = Field(None, description="Type of the benefit", example="Laptop")
    value: float = Field(..., description="Value of the benefit", example=1500.00)
    supplier: Optional[str] = Field(None, description="Supplier of the benefit", example="TechStore")
    particularities: Optional[str] = Field(None, description="Particularities of the benefit", example="Company laptop for work")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class BenefitsInKindUpdate(BaseModel):
    """Schema for updating benefits in kind."""
    start_date: Optional[str] = Field(None, alias="startDate", description="Start date of the benefits in kind", example="2024-01-01")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the benefits in kind", example="2024-12-31")
    benefit_inkind_type: Optional[BenefitInKindTypeCreate] = Field(None, alias="benefitInKindType", description="Benefit in kind type")
    brand: Optional[str] = Field(None, description="Brand of the benefit", example="Apple")
    type: Optional[str] = Field(None, description="Type of the benefit", example="Laptop")
    value: Optional[float] = Field(None, description="Value of the benefit", example=1500.00)
    supplier: Optional[str] = Field(None, description="Supplier of the benefit", example="TechStore")
    particularities: Optional[str] = Field(None, description="Particularities of the benefit", example="Company laptop for work")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"
