from pandera.typing import Series
import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any, Set
from brynq_sdk_functions import BrynQPanderaDataFrameModel, Functions
from ..utils import flat_to_nested_with_metadata
from .base import MetadataWithKey

class AbsenceGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Absence data returned from Loket API.
    An Absence represents a period of absence for an employee.
    """
    # Main absence fields
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the absence", alias="id")

    # Cause of absence
    cause_of_absence_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The key of the cause of the absence", alias="causeOfAbsence.key", nullable=True)
    cause_of_absence_value: Series[str] = pa.Field(coerce=True, description="Description of the cause of the absence", alias="causeOfAbsence.value", nullable=True)

    # Basic absence information
    hours_worked_on_first_day_of_absence: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The number of hours worked on the first day of the absence", alias="hoursWorkedOnFirstDayOfAbsence", nullable=True)

    # Action to be taken by occupational health and safety service
    action_to_be_taken_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The key of the desired action to be taken", alias="actionToBeTakenByOccupationalHealthAndSafetyService.key", nullable=True)
    action_to_be_taken_value: Series[str] = pa.Field(coerce=True, description="Description of the desired action", alias="actionToBeTakenByOccupationalHealthAndSafetyService.value", nullable=True)

    # Expected duration
    expected_duration_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The key of the expected duration", alias="expectedDuration.key", nullable=True)
    expected_duration_value: Series[str] = pa.Field(coerce=True, description="Description of the expected duration", alias="expectedDuration.value", nullable=True)

    # Employment relationship and liability
    is_disrupted_employment_relationship: Series[bool] = pa.Field(coerce=True, description="Indicates whether the employment relationship is disrupted", alias="isDisruptedEmploymentRelationship", nullable=True)
    is_third_party_liability: Series[bool] = pa.Field(coerce=True, description="Indicates whether a third party is liable", alias="isThirdPartyLiability", nullable=True)

    # Accident type
    accident_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The key of the accident type", alias="accidentType.key", nullable=True)
    accident_type_value: Series[str] = pa.Field(coerce=True, description="Description of the accident type", alias="accidentType.value", nullable=True)

    # Work related illness and maternity
    is_work_related_illness: Series[bool] = pa.Field(coerce=True, description="Indicates work-related illness", alias="isWorkRelatedIllness", nullable=True)
    expected_date_of_childbirth: Series[str] = pa.Field(coerce=True, description="Expected date of childbirth", alias="expectedDateOfChildbirth", nullable=True)
    expected_end_date_of_maternity_leave: Series[str] = pa.Field(coerce=True, description="Expected end date of maternity leave", alias="expectedEndDateOfMaternityLeave", nullable=True)

    # Recovery and mobility
    has_mobility_issue: Series[bool] = pa.Field(coerce=True, description="Indicates whether the employee has mobility issues", alias="hasMobilityIssue", nullable=True)
    is_recovered_within_two_weeks: Series[bool] = pa.Field(coerce=True, description="Indicates whether the employee is recovered within two weeks", alias="isRecoveredWithinTwoWeeks", nullable=True)
    is_hospitalised: Series[bool] = pa.Field(coerce=True, description="Indicates whether the employee is hospitalised", alias="isHospitalised", nullable=True)

    # Comments
    comments: Series[str] = pa.Field(coerce=True, description="Free text field for relevant information", alias="comments", nullable=True)

    # Contact information
    contact_information_start_date: Series[str] = pa.Field(coerce=True, description="Start date of contact information", alias="contactInformation.startDate", nullable=True)
    contact_information_end_date: Series[str] = pa.Field(coerce=True, description="End date of contact information", alias="contactInformation.endDate", nullable=True)
    contact_information_location_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Location type key", alias="contactInformation.locationType.key", nullable=True)
    contact_information_location_type_value: Series[str] = pa.Field(coerce=True, description="Location type value", alias="contactInformation.locationType.value", nullable=True)
    contact_information_name: Series[str] = pa.Field(coerce=True, description="Name of the institute", alias="contactInformation.name", nullable=True)
    contact_information_street: Series[str] = pa.Field(coerce=True, description="Street name", alias="contactInformation.street", nullable=True)
    contact_information_city: Series[str] = pa.Field(coerce=True, description="City name", alias="contactInformation.city", nullable=True)
    contact_information_house_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="House number", alias="contactInformation.houseNumber", nullable=True)
    contact_information_house_number_addition: Series[str] = pa.Field(coerce=True, description="House number addition", alias="contactInformation.houseNumberAddition", nullable=True)
    contact_information_further_indication_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Further indication key", alias="contactInformation.furtherIndication.key", nullable=True)
    contact_information_further_indication_value: Series[str] = pa.Field(coerce=True, description="Further indication value", alias="contactInformation.furtherIndication.value", nullable=True)
    contact_information_postal_code: Series[str] = pa.Field(coerce=True, description="Postal code", alias="contactInformation.postalCode", nullable=True)
    contact_information_country_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Country key", alias="contactInformation.country.key", nullable=True)
    contact_information_country_value: Series[str] = pa.Field(coerce=True, description="Country value", alias="contactInformation.country.value", nullable=True)
    contact_information_phone_number: Series[str] = pa.Field(coerce=True, description="Phone number", alias="contactInformation.phoneNumber", nullable=True)

    # Case manager
    case_manager_name: Series[str] = pa.Field(coerce=True, description="Name of the case manager", alias="caseManager.name", nullable=True)
    case_manager_function: Series[str] = pa.Field(coerce=True, description="Function of the case manager", alias="caseManager.function", nullable=True)
    case_manager_organization: Series[str] = pa.Field(coerce=True, description="Organization of the case manager", alias="caseManager.organization", nullable=True)
    case_manager_phone_number: Series[str] = pa.Field(coerce=True, description="Phone number of the case manager", alias="caseManager.phoneNumber", nullable=True)

    # Reintegration
    reintegration_goal_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Reintegration goal key", alias="reintegration.reintegrationGoal.key", nullable=True)
    reintegration_goal_value: Series[str] = pa.Field(coerce=True, description="Reintegration goal value", alias="reintegration.reintegrationGoal.value", nullable=True)
    reintegration_date_of_finalizing_plan: Series[str] = pa.Field(coerce=True, description="Date of finalizing plan of action", alias="reintegration.dateOfFinalizingPlanOfAction", nullable=True)

    # Progress
    progress_start_date: Series[str] = pa.Field(coerce=True, description="Start date of progress", alias="progress.startDate", nullable=True)
    progress_current_incapacity_percentage: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Current incapacity percentage", alias="progress.currentIncapacityPercentage", nullable=True)

    # End of absence
    end_of_absence_date: Series[str] = pa.Field(coerce=True, description="The last day of the absence", alias="endOfAbsence.date", nullable=True)
    end_of_absence_reason_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The key of the reason why the absence ended", alias="endOfAbsence.reason.key", nullable=True)
    end_of_absence_reason_value: Series[str] = pa.Field(coerce=True, description="Description of the reason why the absence ended", alias="endOfAbsence.reason.value", nullable=True)

    # Fields that may come as full objects (not normalized by pd.json_normalize)
    cause_of_absence: Series[str] = pa.Field(coerce=True, description="Cause of absence object", alias="causeOfAbsence", nullable=True)
    action_to_be_taken: Series[str] = pa.Field(coerce=True, description="Action to be taken object", alias="actionToBeTakenByOccupationalHealthAndSafetyService", nullable=True)
    expected_duration: Series[str] = pa.Field(coerce=True, description="Expected duration object", alias="expectedDuration", nullable=True)
    accident_type: Series[str] = pa.Field(coerce=True, description="Accident type object", alias="accidentType", nullable=True)
    contact_information: Series[str] = pa.Field(coerce=True, description="Contact information object", alias="contactInformation", nullable=True)
    case_manager: Series[str] = pa.Field(coerce=True, description="Case manager object", alias="caseManager", nullable=True)
    reintegration: Series[str] = pa.Field(coerce=True, description="Reintegration object", alias="reintegration", nullable=True)
    progress: Series[str] = pa.Field(coerce=True, description="Progress object", alias="progress", nullable=True)
    end_of_absence: Series[str] = pa.Field(coerce=True, description="End of absence object", alias="endOfAbsence", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


# ==================== CREATE ABSENCE SCHEMAS ====================

class ContactInformation(BaseModel):
    """Contact information for absence."""
    start_date: str = Field(..., alias="startDate", description="Start date of the contact information")
    end_date: Optional[str] = Field(None, alias="endDate", description="End date of the contact information")
    location_type: Optional[MetadataWithKey] = Field(None, alias="locationType", description="Location type")
    name: Optional[str] = Field(None, description="Name of the institute", max_length=70)
    street: str = Field(..., description="Street name", max_length=24)
    city: str = Field(..., description="City", max_length=24)
    house_number: int = Field(..., alias="houseNumber", description="House number")
    house_number_addition: Optional[str] = Field(None, alias="houseNumberAddition", description="House number addition", max_length=4)
    further_indication: Optional[MetadataWithKey] = Field(None, alias="furtherIndication", description="Further indication")
    postal_code: str = Field(..., alias="postalCode", description="Postal code", max_length=9)
    country: MetadataWithKey = Field(..., description="Country")
    phone_number: Optional[str] = Field(None, alias="phoneNumber", description="Phone number", max_length=15)

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class CaseManager(BaseModel):
    """Case manager information."""
    name: str = Field(..., description="Name of the case manager", max_length=25)
    function: Optional[str] = Field(None, description="Function of the case manager", max_length=50)
    organization: Optional[str] = Field(None, description="Organization of the case manager", max_length=70)
    phone_number: Optional[str] = Field(None, alias="phoneNumber", description="Phone number", max_length=15)

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class Reintegration(BaseModel):
    """Reintegration information."""
    reintegration_goal: MetadataWithKey = Field(..., alias="reintegrationGoal", description="Reintegration goal")
    date_of_finalizing_plan_of_action: str = Field(..., alias="dateOfFinalizingPlanOfAction", description="Date of finalizing plan of action")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class Progress(BaseModel):
    """Progress information."""
    start_date: str = Field(..., alias="startDate", description="Start date of the incapacity percentage")
    current_incapacity_percentage: int = Field(..., alias="currentIncapacityPercentage", description="Current incapacity percentage", ge=1, le=100)

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"

# Prefix → target alias (nested object name)
PREFIX_MAP: Dict[str, str] = {
    "contact_information": "contactInformation",
    "case_manager": "caseManager",
    "reintegration": "reintegration",
    "progress": "progress",
}

# Root level fields expecting MetadataWithKey (snake_case)
ROOT_METADATA_FIELDS: Set[str] = {
    "cause_of_absence",
    "action_to_be_taken_by_occupational_health_and_safety_service",
    "expected_duration",
    "accident_type",
}

# Nested level fields expecting MetadataWithKey (prefix → field set)
NESTED_METADATA_FIELDS: Dict[str, Set[str]] = {
    "contact_information": {"location_type", "further_indication", "country"},
    "reintegration": {"reintegration_goal"},
    # No metadata fields for case_manager and progress
}

class AbsenceCreate(BaseModel):
    """Schema for creating an absence."""
    cause_of_absence: MetadataWithKey = Field(..., alias="causeOfAbsence", description="Cause of the absence")
    hours_worked_on_first_day_of_absence: Optional[int] = Field(None, alias="hoursWorkedOnFirstDayOfAbsence", description="Hours worked on first day", example=4, ge=1, le=8)
    action_to_be_taken_by_occupational_health_and_safety_service: MetadataWithKey = Field(..., alias="actionToBeTakenByOccupationalHealthAndSafetyService", description="Action to be taken")
    expected_duration: Optional[MetadataWithKey] = Field(None, alias="expectedDuration", description="Expected duration")
    is_disrupted_employment_relationship: bool = Field(..., alias="isDisruptedEmploymentRelationship", description="Is employment relationship disrupted", example=True)
    is_third_party_liability: Optional[bool] = Field(None, alias="isThirdPartyLiability", description="Is third party liability", example=False)
    accident_type: Optional[MetadataWithKey] = Field(None, alias="accidentType", description="Accident type")
    is_work_related_illness: bool = Field(..., alias="isWorkRelatedIllness", description="Is work related illness", example=False)
    expected_date_of_childbirth: Optional[str] = Field(None, alias="expectedDateOfChildbirth", description="Expected date of childbirth", example="2024-06-15")
    expected_end_date_of_maternity_leave: Optional[str] = Field(None, alias="expectedEndDateOfMaternityLeave", description="Expected end date of maternity leave", example="2024-09-15")
    has_mobility_issue: Optional[bool] = Field(None, alias="hasMobilityIssue", description="Has mobility issue", example=False)
    is_recovered_within_two_weeks: bool = Field(..., alias="isRecoveredWithinTwoWeeks", description="Is recovered within two weeks", example=True)
    comments: Optional[str] = Field(None, description="Comments", example="Employee reported sick with flu symptoms", max_length=4000)
    is_hospitalised: Optional[bool] = Field(None, alias="isHospitalised", description="Is hospitalised", example=False)
    contact_information: Optional[ContactInformation] = Field(None, alias="contactInformation", description="Contact information")
    case_manager: Optional[CaseManager] = Field(None, alias="caseManager", description="Case manager")
    reintegration: Optional[Reintegration] = Field(None, description="Reintegration")
    progress: Optional[Progress] = Field(None, description="Progress")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using the generic function from brynq_sdk_functions.
        """
        return flat_to_nested_with_metadata(
            values=values,
            prefix_map=PREFIX_MAP,
            root_metadata_fields=ROOT_METADATA_FIELDS,
            nested_metadata_fields=NESTED_METADATA_FIELDS
        )

class AbsenceUpdate(BaseModel):
    """Schema for updating an absence."""
    cause_of_absence: Optional[MetadataWithKey] = Field(None, alias="causeOfAbsence", description="Cause of the absence")
    hours_worked_on_first_day_of_absence: Optional[int] = Field(None, alias="hoursWorkedOnFirstDayOfAbsence", description="Hours worked on first day", example=4, ge=1, le=8)
    action_to_be_taken_by_occupational_health_and_safety_service: Optional[MetadataWithKey] = Field(None, alias="actionToBeTakenByOccupationalHealthAndSafetyService", description="Action to be taken")
    expected_duration: Optional[MetadataWithKey] = Field(None, alias="expectedDuration", description="Expected duration")
    is_disrupted_employment_relationship: Optional[bool] = Field(None, alias="isDisruptedEmploymentRelationship", description="Is employment relationship disrupted", example=True)
    is_third_party_liability: Optional[bool] = Field(None, alias="isThirdPartyLiability", description="Is third party liability", example=False)
    accident_type: Optional[MetadataWithKey] = Field(None, alias="accidentType", description="Accident type")
    is_work_related_illness: Optional[bool] = Field(None, alias="isWorkRelatedIllness", description="Is work related illness", example=False)
    expected_date_of_childbirth: Optional[str] = Field(None, alias="expectedDateOfChildbirth", description="Expected date of childbirth", example="2024-06-15")
    expected_end_date_of_maternity_leave: Optional[str] = Field(None, alias="expectedEndDateOfMaternityLeave", description="Expected end date of maternity leave", example="2024-09-15")
    has_mobility_issue: Optional[bool] = Field(None, alias="hasMobilityIssue", description="Has mobility issue", example=False)
    is_recovered_within_two_weeks: Optional[bool] = Field(None, alias="isRecoveredWithinTwoWeeks", description="Is recovered within two weeks", example=True)
    comments: Optional[str] = Field(None, description="Comments", example="Employee reported sick with flu symptoms", max_length=4000)
    is_hospitalised: Optional[bool] = Field(None, alias="isHospitalised", description="Is hospitalised", example=False)
    contact_information: Optional[ContactInformation] = Field(None, alias="contactInformation", description="Contact information")
    case_manager: Optional[CaseManager] = Field(None, alias="caseManager", description="Case manager")
    reintegration: Optional[Reintegration] = Field(None, description="Reintegration")
    progress: Optional[Progress] = Field(None, description="Progress")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat dictionary to nested structure using the generic function from brynq_sdk_functions.
        """
        return flat_to_nested_with_metadata(
            values=values,
            prefix_map=PREFIX_MAP,
            root_metadata_fields=ROOT_METADATA_FIELDS,
            nested_metadata_fields=NESTED_METADATA_FIELDS
        )
