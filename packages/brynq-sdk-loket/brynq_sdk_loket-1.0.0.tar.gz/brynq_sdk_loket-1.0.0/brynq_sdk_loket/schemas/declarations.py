from pandera.typing import Series
import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any, List, Set
from brynq_sdk_functions import BrynQPanderaDataFrameModel, Functions
from ..utils import flat_to_nested_with_metadata



class DeclarationGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Declaration data returned from Loket API.
    A Declaration represents an expense or travel declaration for an employee.
    """
    # Main declaration fields
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the declaration", alias="id")

    # Payroll component nested fields
    payroll_component_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payroll component key", alias="payrollComponent.key")
    payroll_component_description: Series[str] = pa.Field(coerce=True, description="Payroll component description", alias="payrollComponent.description")
    payroll_component_deviating_description: Series[str] = pa.Field(coerce=True, description="Payroll component deviating description", alias="payrollComponent.deviatingDescription", nullable=True)

    # Deduction or payment nested fields
    deduction_or_payment_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Deduction or payment key", alias="payrollComponent.deductionOrPayment.key")
    deduction_or_payment_value: Series[str] = pa.Field(coerce=True, description="Deduction or payment value", alias="payrollComponent.deductionOrPayment.value")

    # Route type nested fields
    route_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Route type key", alias="payrollComponent.routeType.key")
    route_type_value: Series[str] = pa.Field(coerce=True, description="Route type value", alias="payrollComponent.routeType.value")

    # Declaration details
    calculated_distance_by_routing_service: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Calculated distance by routing service in kilometers", alias="calculatedDistanceByRoutingService", nullable=True)
    number_of_units: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Number of units", alias="numberOfUnits")
    declaration_date: Series[str] = pa.Field(coerce=True, description="Declaration date", alias="declarationDate")
    declaration_comment: Series[str] = pa.Field(coerce=True, description="Declaration comment", alias="declarationComment", nullable=True)

    # Declaration status nested fields
    declaration_status_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Declaration status key", alias="declarationStatus.key")
    declaration_status_value: Series[str] = pa.Field(coerce=True, description="Declaration status value", alias="declarationStatus.value")

    # Dates
    date_of_submission_by_employee: Series[str] = pa.Field(coerce=True, description="Date of submission by employee", alias="dateOfSubmissionByEmployee", nullable=True)
    date_of_last_change_by_employee: Series[str] = pa.Field(coerce=True, description="Date of last change by employee", alias="dateOfLastChangeByEmployee", nullable=True)

    # Processed in payroll period nested fields
    processed_year: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Processed year", alias="processedInPayrollPeriod.year", nullable=True)
    processed_period_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Processed period number", alias="processedInPayrollPeriod.periodNumber", nullable=True)
    processed_period_start_date: Series[str] = pa.Field(coerce=True, description="Processed period start date", alias="processedInPayrollPeriod.periodStartDate", nullable=True)
    processed_period_end_date: Series[str] = pa.Field(coerce=True, description="Processed period end date", alias="processedInPayrollPeriod.periodEndDate", nullable=True)

    # Route information
    reason_for_deviating_from_calculated_distance: Series[str] = pa.Field(coerce=True, description="Reason for deviating from calculated distance", alias="reasonForDeviatingFromCalculatedDistance", nullable=True)

    # Route points (simplified - will contain JSON string representation)
    route: Series[str] = pa.Field(coerce=True, description="Route points as JSON string", alias="route", nullable=True)

    # Employment information nested fields (for employer-level declarations)
    employment_information_id: Series[str] = pa.Field(coerce=True, description="Employment information ID", alias="employmentInformation.id", nullable=True)
    employment_information_employee_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Employment information employee number", alias="employmentInformation.employeeNumber", nullable=True)
    employment_information_first_name: Series[str] = pa.Field(coerce=True, description="Employment information first name", alias="employmentInformation.firstName", nullable=True)
    employment_information_formatted_name: Series[str] = pa.Field(coerce=True, description="Employment information formatted name", alias="employmentInformation.formattedName", nullable=True)
    employment_information_income_relationship_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Employment information income relationship number", alias="employmentInformation.incomeRelationshipNumber", nullable=True)
    employment_information_photo: Series[str] = pa.Field(coerce=True, description="Employment information photo URL", alias="employmentInformation.photo", nullable=True)

    # Payroll administration nested fields
    payroll_administration_id: Series[str] = pa.Field(coerce=True, description="Payroll administration ID", alias="employmentInformation.payrollAdministration.id", nullable=True)
    payroll_administration_name: Series[str] = pa.Field(coerce=True, description="Payroll administration name", alias="employmentInformation.payrollAdministration.name", nullable=True)
    payroll_administration_client_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payroll administration client number", alias="employmentInformation.payrollAdministration.clientNumber", nullable=True)
    payroll_administration_description: Series[str] = pa.Field(coerce=True, description="Payroll administration description", alias="employmentInformation.payrollAdministration.description", nullable=True)

    # Function nested fields
    function_key: Series[str] = pa.Field(coerce=True, description="Function key", alias="employmentInformation.function.key", nullable=True)
    function_description: Series[str] = pa.Field(coerce=True, description="Function description", alias="employmentInformation.function.description", nullable=True)
    function_group: Series[str] = pa.Field(coerce=True, description="Function group", alias="employmentInformation.function.group", nullable=True)

    # Department nested fields
    department_key: Series[str] = pa.Field(coerce=True, description="Department key", alias="employmentInformation.department.key", nullable=True)
    department_code: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Department code", alias="employmentInformation.department.code", nullable=True)
    department_description: Series[str] = pa.Field(coerce=True, description="Department description", alias="employmentInformation.department.description", nullable=True)

    # Fields that may come as full objects (not normalized by pd.json_normalize)
    employment_information: Series[str] = pa.Field(coerce=True, description="Employment information object", alias="employmentInformation", nullable=True)
    payroll_component: Series[str] = pa.Field(coerce=True, description="Payroll component object", alias="payrollComponent", nullable=True)
    declaration_status: Series[str] = pa.Field(coerce=True, description="Declaration status object", alias="declarationStatus", nullable=True)
    processed_in_payroll_period: Series[str] = pa.Field(coerce=True, description="Processed in payroll period object", alias="processedInPayrollPeriod", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


# ==================== CREATE DECLARATION SCHEMAS ====================

# Prefix → target alias (nested object name)
PREFIX_MAP: Dict[str, str] = {
    "route": "route",
}

# Root level fields expecting MetadataWithKey (snake_case)
ROOT_METADATA_FIELDS: Set[str] = {
    "payroll_component",
}

# Nested level fields expecting MetadataWithKey (prefix → field set)
NESTED_METADATA_FIELDS: Dict[str, Set[str]] = {
    # No nested metadata fields for declarations
}


class PayrollComponent(BaseModel):
    """Payroll component information."""
    key: int = Field(..., description="Payroll component key")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class PointOfInterest(BaseModel):
    """Point of interest information."""
    name: Optional[str] = Field(None, description="Name of the point of interest", max_length=100)

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class Address(BaseModel):
    """Address information."""
    freeform_address: Optional[str] = Field(None, alias="freeformAddress", description="Freeform address", max_length=255)
    country_code: Optional[str] = Field(None, alias="countryCode", description="Country code", max_length=2)

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class Position(BaseModel):
    """Position information."""
    latitude: Optional[float] = Field(None, description="Latitude", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="Longitude", ge=-180, le=180)

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class RoutePoint(BaseModel):
    """Route point information."""
    point_of_interest: Optional[PointOfInterest] = Field(None, alias="pointOfInterest", description="Point of interest")
    address: Optional[Address] = Field(None, description="Address")
    position: Optional[Position] = Field(None, description="Position")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class DeclarationCreate(BaseModel):
    """Schema for creating a declaration."""
    payroll_component: PayrollComponent = Field(..., alias="payrollComponent", description="Payroll component")
    calculated_distance_by_routing_service: Optional[int] = Field(None, alias="calculatedDistanceByRoutingService", description="Calculated distance by routing service", example=15, ge=0)
    number_of_units: int = Field(..., alias="numberOfUnits", description="Number of units", example=1, ge=1)
    declaration_date: str = Field(..., alias="declarationDate", description="Declaration date", example="2024-01-15")
    declaration_comment: Optional[str] = Field(None, alias="declarationComment", description="Declaration comment", example="Business trip to client", max_length=1000)
    reason_for_deviating_from_calculated_distance: Optional[str] = Field(None, alias="reasonForDeviatingFromCalculatedDistance", description="Reason for deviating from calculated distance", example="Traffic congestion", max_length=500)
    route: Optional[List[RoutePoint]] = Field(None, description="Route points")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using the generic function from brynq_sdk_functions.
        Additionally, normalize 'route' to a list of RoutePoint-like dicts when a single object is provided
        or when flattened keys are present.
        """
        out = flat_to_nested_with_metadata(
            values=values,
            prefix_map=PREFIX_MAP,
            root_metadata_fields=ROOT_METADATA_FIELDS,
            nested_metadata_fields=NESTED_METADATA_FIELDS
        )

        def _convert_route_point(item: Dict[str, Any]) -> Dict[str, Any]:
            # Already nested or not a dict
            if item is None or not isinstance(item, Dict):
                return item
            if any(k in item for k in ("pointOfInterest", "address", "position")):
                return item

            point: Dict[str, Any] = {}

            poi_name = item.get("pointOfInterestName")
            if poi_name is not None:
                point["pointOfInterest"] = {"name": poi_name}

            addr_free = item.get("addressFreeform")
            addr_country = item.get("addressCountryCode")
            if addr_free is not None or addr_country is not None:
                addr: Dict[str, Any] = {}
                if addr_free is not None:
                    addr["freeformAddress"] = addr_free
                if addr_country is not None:
                    addr["countryCode"] = addr_country
                point["address"] = addr

            lat = item.get("positionLatitude")
            lon = item.get("positionLongitude")
            if lat is not None or lon is not None:
                pos: Dict[str, Any] = {}
                if lat is not None:
                    pos["latitude"] = lat
                if lon is not None:
                    pos["longitude"] = lon
                point["position"] = pos

            # Preserve any other keys
            for k, v in item.items():
                if k not in {"pointOfInterestName", "addressFreeform", "addressCountryCode", "positionLatitude", "positionLongitude"}:
                    point[k] = v

            return point

        if "route" in out and out["route"] is not None:
            route_val = out["route"]
            if isinstance(route_val, Dict):
                out["route"] = [_convert_route_point(route_val)]
            elif isinstance(route_val, list):
                out["route"] = [_convert_route_point(x) for x in route_val]

        return out


class DeclarationUpdate(BaseModel):
    """Schema for updating a declaration."""
    payroll_component: Optional[PayrollComponent] = Field(None, alias="payrollComponent", description="Payroll component")
    calculated_distance_by_routing_service: Optional[int] = Field(None, alias="calculatedDistanceByRoutingService", description="Calculated distance by routing service", example=15, ge=0)
    number_of_units: Optional[int] = Field(None, alias="numberOfUnits", description="Number of units", example=1, ge=1)
    declaration_date: Optional[str] = Field(None, alias="declarationDate", description="Declaration date", example="2024-01-15")
    declaration_comment: Optional[str] = Field(None, alias="declarationComment", description="Declaration comment", example="Business trip to client", max_length=1000)
    reason_for_deviating_from_calculated_distance: Optional[str] = Field(None, alias="reasonForDeviatingFromCalculatedDistance", description="Reason for deviating from calculated distance", example="Traffic congestion", max_length=500)
    route: Optional[List[RoutePoint]] = Field(None, description="Route points")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using the generic function from brynq_sdk_functions.
        Additionally, normalize 'route' to a list of RoutePoint-like dicts when a single object is provided
        or when flattened keys are present.
        """
        out = flat_to_nested_with_metadata(
            values=values,
            prefix_map=PREFIX_MAP,
            root_metadata_fields=ROOT_METADATA_FIELDS,
            nested_metadata_fields=NESTED_METADATA_FIELDS
        )

        def _convert_route_point(item: Dict[str, Any]) -> Dict[str, Any]:
            # Already nested or not a dict
            if item is None or not isinstance(item, Dict):
                return item
            if any(k in item for k in ("pointOfInterest", "address", "position")):
                return item

            point: Dict[str, Any] = {}

            poi_name = item.get("pointOfInterestName")
            if poi_name is not None:
                point["pointOfInterest"] = {"name": poi_name}

            addr_free = item.get("addressFreeform")
            addr_country = item.get("addressCountryCode")
            if addr_free is not None or addr_country is not None:
                addr: Dict[str, Any] = {}
                if addr_free is not None:
                    addr["freeformAddress"] = addr_free
                if addr_country is not None:
                    addr["countryCode"] = addr_country
                point["address"] = addr

            lat = item.get("positionLatitude")
            lon = item.get("positionLongitude")
            if lat is not None or lon is not None:
                pos: Dict[str, Any] = {}
                if lat is not None:
                    pos["latitude"] = lat
                if lon is not None:
                    pos["longitude"] = lon
                point["position"] = pos

            # Preserve any other keys
            for k, v in item.items():
                if k not in {"pointOfInterestName", "addressFreeform", "addressCountryCode", "positionLatitude", "positionLongitude"}:
                    point[k] = v

            return point

        if "route" in out and out["route"] is not None:
            route_val = out["route"]
            if isinstance(route_val, Dict):
                out["route"] = [_convert_route_point(route_val)]
            elif isinstance(route_val, list):
                out["route"] = [_convert_route_point(x) for x in route_val]

        return out


class DeclarationReviewItem(BaseModel):
    """Schema for a single declaration review item."""
    id: str = Field(..., description="Declaration ID")
    action: str = Field(..., description="Review action (accept/reject)")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class DeclarationProcessItem(BaseModel):
    """Schema for a single declaration process item."""
    id: str = Field(..., description="Declaration ID")
    payroll_period_id: int = Field(..., alias="payrollPeriodId", description="Payroll period ID")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class DeclarationAuditTrailGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Declaration Audit Trail data returned from Loket API.
    An Audit Trail represents the history of changes made to a declaration.
    """
    # Main audit trail fields
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the audit trail entry", alias="id")

    # Status nested fields
    status_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Status key", alias="status.key")
    status_value: Series[str] = pa.Field(coerce=True, description="Status value", alias="status.value")

    # Performed by nested fields
    performed_by_id: Series[str] = pa.Field(coerce=True, description="ID of the person who performed the action", alias="performedBy.id")
    performed_by_initials: Series[str] = pa.Field(coerce=True, description="Initials of the person who performed the action", alias="performedBy.initials")
    performed_by_prefix: Series[str] = pa.Field(coerce=True, description="Prefix of the person who performed the action", alias="performedBy.prefix", nullable=True)
    performed_by_last_name: Series[str] = pa.Field(coerce=True, description="Last name of the person who performed the action", alias="performedBy.lastName")
    performed_by_formatted_name: Series[str] = pa.Field(coerce=True, description="Formatted name of the person who performed the action", alias="performedBy.formattedName")

    # Audit trail details
    performed_on: Series[str] = pa.Field(coerce=True, description="Date when the action was performed", alias="performedOn")
    comment: Series[str] = pa.Field(coerce=True, description="Comment about the action performed", alias="comment", nullable=True)

    # Fields that may come as full objects (not normalized by pd.json_normalize)
    status: Series[str] = pa.Field(coerce=True, description="Status object", alias="status", nullable=True)
    performed_by: Series[str] = pa.Field(coerce=True, description="Performed by object", alias="performedBy", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True
