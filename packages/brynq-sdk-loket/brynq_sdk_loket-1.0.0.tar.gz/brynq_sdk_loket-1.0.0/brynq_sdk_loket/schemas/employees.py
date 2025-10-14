from pandera.typing import Series
import pandera as pa
import pandas as pd
from pydantic import BaseModel, Field,model_validator
from typing import Optional,Dict,Any
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from .base import MetadataWithKey, MetadataWithKeyAndValue, MetadataWithKeyAndIsoCode, CountryWithIsoCode


class EmployeeGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Employee data returned from Loket API.
    An Employee represents a person working for an employer in the Loket system.
    """
    # Main employee fields
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the employee", alias="id")
    employee_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The employee number", alias="employeeNumber")

    # Personal details nested fields
    first_name: Series[str] = pa.Field(coerce=True, description="The first name of the employee", alias="personalDetails.firstName", nullable=True)
    last_name: Series[str] = pa.Field(coerce=True, description="The last name of the employee", alias="personalDetails.lastName")
    prefix: Series[str] = pa.Field(coerce=True, description="The prefix of the employee", alias="personalDetails.prefix", nullable=True)
    initials: Series[str] = pa.Field(coerce=True, description="The initials of the employee", alias="personalDetails.initials")
    last_name_partner: Series[str] = pa.Field(coerce=True, description="The last name partner of the employee", alias="personalDetails.lastNamePartner", nullable=True)
    prefix_partner: Series[str] = pa.Field(coerce=True, description="The prefix partner of the employee", alias="personalDetails.prefixPartner", nullable=True)
    formatted_name: Series[str] = pa.Field(coerce=True, description="The formatted name of the employee", alias="personalDetails.formattedName")
    date_of_birth: Series[str] = pa.Field(coerce=True, description="The date of birth of the employee", alias="personalDetails.dateOfBirth")
    place_of_birth: Series[str] = pa.Field(coerce=True, description="The place of birth of the employee", alias="personalDetails.placeOfBirth", nullable=True)
    date_of_death: Series[str] = pa.Field(coerce=True, description="The date of death of the employee", alias="personalDetails.dateOfDeath", nullable=True)
    aow_date: Series[str] = pa.Field(coerce=True, description="The AOW date of the employee", alias="personalDetails.aowDate")
    photo: Series[str] = pa.Field(coerce=True, description="The photo URL of the employee", alias="personalDetails.photo", nullable=True)

    # Metadata objects
    how_to_format_last_name_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="How to format last name key", alias="personalDetails.howToFormatLastName.key")
    how_to_format_last_name_value: Series[str] = pa.Field(coerce=True, description="How to format last name value", alias="personalDetails.howToFormatLastName.value")
    title_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Title key", alias="personalDetails.title.key", nullable=True)
    title_value: Series[str] = pa.Field(coerce=True, description="Title value", alias="personalDetails.title.value", nullable=True)
    nationality_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Nationality key", alias="personalDetails.nationality.key", nullable=True)
    nationality_value: Series[str] = pa.Field(coerce=True, description="Nationality value", alias="personalDetails.nationality.value", nullable=True)
    gender_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Gender key", alias="personalDetails.gender.key")
    gender_value: Series[str] = pa.Field(coerce=True, description="Gender value", alias="personalDetails.gender.value")
    civil_status_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Civil status key", alias="personalDetails.civilStatus.key", nullable=True)
    civil_status_value: Series[str] = pa.Field(coerce=True, description="Civil status value", alias="personalDetails.civilStatus.value", nullable=True)

    # Contact information nested fields
    phone_number: Series[str] = pa.Field(coerce=True, description="The phone number of the employee", alias="contactInformation.phoneNumber", nullable=True)
    mobile_phone_number: Series[str] = pa.Field(coerce=True, description="The mobile phone number of the employee", alias="contactInformation.mobilePhoneNumber", nullable=True)
    fax_number: Series[str] = pa.Field(coerce=True, description="The fax number of the employee", alias="contactInformation.faxNumber", nullable=True)
    email_address: Series[str] = pa.Field(coerce=True, description="The email address of the employee", alias="contactInformation.emailAddress", nullable=True)
    business_phone_number: Series[str] = pa.Field(coerce=True, description="The business phone number of the employee", alias="contactInformation.businessPhoneNumber", nullable=True)
    business_mobile_phone_number: Series[str] = pa.Field(coerce=True, description="The business mobile phone number of the employee", alias="contactInformation.businessMobilePhoneNumber", nullable=True)
    business_email_address: Series[str] = pa.Field(coerce=True, description="The business email address of the employee", alias="contactInformation.businessEmailAddress", nullable=True)

    # Identity document nested fields
    type_of_document_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Type of document key", alias="identityDocument.typeOfDocument.key", nullable=True)
    type_of_document_value: Series[str] = pa.Field(coerce=True, description="Type of document value", alias="identityDocument.typeOfDocument.value", nullable=True)
    document_identification: Series[str] = pa.Field(coerce=True, description="Document identification", alias="identityDocument.documentIdentification", nullable=True)

    # Travel nested fields
    travel_distance_to_work: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Travel distance to work in meters", alias="travel.travelDistanceToWork", nullable=True)
    travel_distance_to_work_in_km: Series[float] = pa.Field(coerce=True, description="Travel distance to work in kilometers", alias="travel.travelDistanceToWorkInKm", nullable=True)

    # Address nested fields
    street: Series[str] = pa.Field(coerce=True, description="The street name", alias="address.street", nullable=True)
    city: Series[str] = pa.Field(coerce=True, description="The city name", alias="address.city", nullable=True)
    house_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The house number", alias="address.houseNumber", nullable=True)
    house_number_addition: Series[str] = pa.Field(coerce=True, description="The house number addition", alias="address.houseNumberAddition", nullable=True)
    further_indication_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Further indication key", alias="address.furtherIndication.key", nullable=True)
    further_indication_value: Series[str] = pa.Field(coerce=True, description="Further indication value", alias="address.furtherIndication.value", nullable=True)
    postal_code: Series[str] = pa.Field(coerce=True, description="The postal code", alias="address.postalCode", nullable=True)
    location: Series[str] = pa.Field(coerce=True, description="The location", alias="address.location", nullable=True)
    country_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The country key", alias="address.country.key", nullable=True)
    country_value: Series[str] = pa.Field(coerce=True, description="The country value", alias="address.country.value", nullable=True)

    # Deviating postal address nested fields
    deviating_street: Series[str] = pa.Field(coerce=True, description="The deviating street name", alias="deviatingPostalAddress.street", nullable=True)
    deviating_city: Series[str] = pa.Field(coerce=True, description="The deviating city name", alias="deviatingPostalAddress.city", nullable=True)
    deviating_house_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The deviating house number", alias="deviatingPostalAddress.houseNumber", nullable=True)
    deviating_house_number_addition: Series[str] = pa.Field(coerce=True, description="The deviating house number addition", alias="deviatingPostalAddress.houseNumberAddition", nullable=True)
    deviating_further_indication_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Deviating further indication key", alias="deviatingPostalAddress.furtherIndication.key", nullable=True)
    deviating_further_indication_value: Series[str] = pa.Field(coerce=True, description="Deviating further indication value", alias="deviatingPostalAddress.furtherIndication.value", nullable=True)
    deviating_postal_code: Series[str] = pa.Field(coerce=True, description="The deviating postal code", alias="deviatingPostalAddress.postalCode", nullable=True)
    deviating_location: Series[str] = pa.Field(coerce=True, description="The deviating location", alias="deviatingPostalAddress.location", nullable=True)
    deviating_country_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The deviating country key", alias="deviatingPostalAddress.country.key", nullable=True)
    deviating_country_value: Series[str] = pa.Field(coerce=True, description="The deviating country value", alias="deviatingPostalAddress.country.value", nullable=True)

    # Additional fields
    exclusion_from_absence_status: Series[bool] = pa.Field(coerce=True, description="Exclusion from absence status", alias="exclusionFromAbsenceStatus")
    status_employee_self_service_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Status employee self service key", alias="statusEmployeeSelfService.key", nullable=True)
    status_employee_self_service_value: Series[str] = pa.Field(coerce=True, description="Status employee self service value", alias="statusEmployeeSelfService.value", nullable=True)
    revoke_employee_self_service_access_on: Series[str] = pa.Field(coerce=True, description="Revoke employee self service access on", alias="revokeEmployeeSelfServiceAccessOn", nullable=True)

    # Fields that come in original camelCase format (not converted by pd.json_normalize)
    status_employee_self_service: Series[str] = pa.Field(coerce=True, description="Status employee self service", alias="statusEmployeeSelfService", nullable=True)
    identity_document: Series[str] = pa.Field(coerce=True, description="Identity document", alias="identityDocument", nullable=True)
    deviating_postal_address: Series[str] = pa.Field(coerce=True, description="Deviating postal address", alias="deviatingPostalAddress", nullable=True)
    personal_details_title: Series[str] = pa.Field(coerce=True, description="Personal details title", alias="personalDetails.title", nullable=True)
    address_further_indication: Series[str] = pa.Field(coerce=True, description="Address further indication", alias="address.furtherIndication", nullable=True)
    address_country_iso_code: Series[str] = pa.Field(coerce=True, description="Address country ISO code", alias="address.country.isoCode", nullable=True)
    personal_details_civil_status: Series[str] = pa.Field(coerce=True, description="Personal details civil status", alias="personalDetails.civilStatus", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True


class PersonalDetails(BaseModel):
    """Personal details nested schema."""
    first_name: Optional[str] = Field(None, alias="firstName", description="The first name, given name, forename or Christian name", max_length=28)
    last_name: Optional[str] = Field(None, alias="lastName", description="The last name, family name or surname", min_length=1, max_length=25)
    prefix: Optional[str] = Field(None, description="The prefix to the last name", max_length=10)
    initials: Optional[str] = Field(None, description="The initials", min_length=1, max_length=6)
    last_name_partner: Optional[str] = Field(None, alias="lastNamePartner", description="The last name of the employee's partner", max_length=25)
    prefix_partner: Optional[str] = Field(None, alias="prefixPartner", description="The prefix to the last name of the employee's partner", max_length=10)
    formatted_name: Optional[str] = Field(None, alias="formattedName", description="The formatted name of the employee")
    date_of_birth: Optional[str] = Field(None, alias="dateOfBirth", description="The date of birth")
    place_of_birth: Optional[str] = Field(None, alias="placeOfBirth", description="The place of birth", max_length=24)
    date_of_death: Optional[str] = Field(None, alias="dateOfDeath", description="The date of death")
    aow_date: Optional[str] = Field(None, alias="aowDate", description="The AOW date of the employee")
    photo: Optional[str] = Field(None, description="The photo URL of the employee")
    how_to_format_last_name: Optional[MetadataWithKeyAndValue] = Field(None, alias="howToFormatLastName", description="Indicates how the system will format the last name")
    title: Optional[MetadataWithKey] = Field(None, description="The title to be used (if any)")
    nationality: Optional[MetadataWithKeyAndValue] = Field(None, description="The nationality")
    gender: Optional[MetadataWithKeyAndValue] = Field(None, description="The gender")
    civil_status: Optional[MetadataWithKeyAndValue] = Field(None, alias="civilStatus", description="The civil/marital status of the employee")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class ContactInformation(BaseModel):
    """Contact information nested schema."""
    phone_number: Optional[str] = Field(None, alias="phoneNumber", description="The phone number of the employee", max_length=15)
    mobile_phone_number: Optional[str] = Field(None, alias="mobilePhoneNumber", description="The mobile phone number of the employee", max_length=15)
    fax_number: Optional[str] = Field(None, alias="faxNumber", description="The fax number to contact this individual", max_length=15)
    email_address: Optional[str] = Field(None, alias="emailAddress", description="The e-mail address of the employee", max_length=255)
    business_phone_number: Optional[str] = Field(None, alias="businessPhoneNumber", description="The business phone number of the employee", max_length=15)
    business_mobile_phone_number: Optional[str] = Field(None, alias="businessMobilePhoneNumber", description="The business mobile phone number of the employee", max_length=15)
    business_email_address: Optional[str] = Field(None, alias="businessEmailAddress", description="The business e-mail address of the employee", max_length=255)

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class IdentityDocument(BaseModel):
    """Identity document nested schema."""
    type_of_document: Optional[MetadataWithKey] = Field(None, alias="typeOfDocument", description="Type of identity document")
    document_identification: Optional[str] = Field(None, alias="documentIdentification", description="Document identification")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class Travel(BaseModel):
    """Travel nested schema."""
    travel_distance_to_work: Optional[int] = Field(None, alias="travelDistanceToWork", description="The one way distance in meters the employee has to travel to work", ge=1)

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"




class Address(BaseModel):
    """Address nested schema."""
    street: Optional[str] = Field(None, description="Streetname of the address", max_length=24)
    city: Optional[str] = Field(None, description="City of the address", max_length=24)
    house_number: Optional[int] = Field(None, alias="houseNumber", description="House number of the address")
    house_number_addition: Optional[str] = Field(None, alias="houseNumberAddition", description="An addition to further specify the house/door/postbox", max_length=4)
    further_indication: Optional[MetadataWithKeyAndValue] = Field(None, alias="furtherIndication", description="Further indication")
    postal_code: Optional[str] = Field(None, alias="postalCode", description="The postal code of the address", min_length=1, max_length=9)
    location: Optional[str] = Field(None, description="The location like to further specify the address", max_length=35)
    country: Optional[CountryWithIsoCode] = Field(None, description="The country")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class DeviatingPostalAddress(BaseModel):
    """Deviating postal address for the employer"""
    street: Optional[str] = Field(None, max_length=24, description="Streetname of the address")
    city: Optional[str] = Field(None, max_length=24, description="City of the address")
    house_number: Optional[int] = Field(None, alias="houseNumber", description="House number of the address")
    house_number_addition: Optional[str] = Field(None, max_length=4, alias="houseNumberAddition", description="An addition to further specify the house/door/postbox")
    further_indication: Optional[MetadataWithKeyAndValue] = Field(None, alias="furtherIndication", description="Further indication for the address")
    postal_code: Optional[str] = Field(None, max_length=9, alias="postalCode", description="The postal code of the address")
    location: Optional[str] = Field(None, max_length=35, description="The location to further specify the address")
    country: Optional[MetadataWithKeyAndIsoCode] = Field(None, description="Country information")
    po_box: Optional[int] = Field(None, alias="poBox", description="Post office box")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class EmployeeUpdate(BaseModel):
    """Schema for updating employee data."""
    employee_number: Optional[int] = Field(None, alias="employeeNumber", description="The employee number to uniquely identify an employee within an employer", example=1001, ge=1)
    personal_details: Optional[PersonalDetails] = Field(None, alias="personalDetails", description="Personal details of the employee")
    citizen_service_number: Optional[int] = Field(None, alias="citizenServiceNumber", description="Citizen service number (BSN)", example=123456789)
    contact_information: Optional[ContactInformation] = Field(None, alias="contactInformation", description="Contact information of the employee")
    identity_document: Optional[IdentityDocument] = Field(None, alias="identityDocument", description="Identity document of the employee")
    travel: Optional[Travel] = Field(None, alias="travel", description="Travel information of the employee")
    address: Optional[Address] = Field(None, alias="address", description="Address of the employee")
    deviating_postal_address: Optional[DeviatingPostalAddress] = Field(None, alias="deviatingPostalAddress", description="Deviating postal address of the employee")
    exclusion_from_absence_status: Optional[bool] = Field(None, alias="exclusionFromAbsenceStatus", description="Indicates whether the employee is excluded for any information of absence", example=False)
    status_employee_self_service: Optional[MetadataWithKeyAndValue] = Field(None, alias="statusEmployeeSelfService", description="Status employee self service")
    id: Optional[str] = Field(None, description="The unique identifier of the employee", example="emp_123456")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"
    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(values, dict):
            return values

        # If already nested, return as-is
        if any(k in values for k in [
            "personal_details", "personalDetails",
            "contact_information", "contactInformation",
            "identity_document", "identityDocument",
            "travel",
            "address",
            "deviating_postal_address", "deviatingPostalAddress",
        ]):
            return values

        data = values.copy()

        def pick(source: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
            out: Dict[str, Any] = {}
            for src, dst in mapping.items():
                if src in source and source[src] is not None:
                    out[dst] = source[src]
            return out

        def build_metadata(src_prefix: str) -> Dict[str, Any]:
            obj: Dict[str, Any] = {}
            direct = data.get(src_prefix)
            if isinstance(direct, dict):
                obj.update({k: v for k, v in direct.items() if v is not None})
            if f"{src_prefix}_key" in data and data[f"{src_prefix}_key"] is not None:
                obj["key"] = data[f"{src_prefix}_key"]
            if f"{src_prefix}_value" in data and data[f"{src_prefix}_value"] is not None:
                obj["value"] = data[f"{src_prefix}_value"]
            if f"{src_prefix}_iso_code" in data and data[f"{src_prefix}_iso_code"] is not None:
                obj["isoCode"] = data[f"{src_prefix}_iso_code"]
            return obj

        result: Dict[str, Any] = {}

        # employeeNumber (flat top-level)
        if data.get("employee_number") is not None:
            result["employeeNumber"] = data["employee_number"]

        # citizenServiceNumber (flat top-level)
        if data.get("citizen_service_number") is not None:
            result["citizenServiceNumber"] = data["citizen_service_number"]

        # exclusionFromAbsenceStatus
        if data.get("exclusion_from_absence_status") is not None:
            result["exclusionFromAbsenceStatus"] = data["exclusion_from_absence_status"]

        # statusEmployeeSelfService (metadata)
        ses = build_metadata("status_employee_self_service")
        if ses:
            result["statusEmployeeSelfService"] = ses

        # id passthrough
        if data.get("id") is not None:
            result["id"] = data["id"]

        # personalDetails
        personal_details: Dict[str, Any] = {}
        personal_details.update(pick(data, {
            "first_name": "firstName",
            "last_name": "lastName",
            "prefix": "prefix",
            "initials": "initials",
            "last_name_partner": "lastNamePartner",
            "prefix_partner": "prefixPartner",
            "formatted_name": "formattedName",
            "date_of_birth": "dateOfBirth",
            "place_of_birth": "placeOfBirth",
            "date_of_death": "dateOfDeath",
            "aow_date": "aowDate",
            "photo": "photo",
        }))
        for meta_src, meta_dst in {
            "how_to_format_last_name": "howToFormatLastName",
            "title": "title",
            "nationality": "nationality",
            "gender": "gender",
            "civil_status": "civilStatus",
        }.items():
            m = build_metadata(meta_src)
            if m:
                personal_details[meta_dst] = m
        if personal_details:
            result["personalDetails"] = personal_details

        # contactInformation
        contact_information = pick(data, {
            "phone_number": "phoneNumber",
            "mobile_phone_number": "mobilePhoneNumber",
            "fax_number": "faxNumber",
            "email_address": "emailAddress",
            "business_phone_number": "businessPhoneNumber",
            "business_mobile_phone_number": "businessMobilePhoneNumber",
            "business_email_address": "businessEmailAddress",
        })
        if contact_information:
            result["contactInformation"] = contact_information

        # identityDocument
        identity_document: Dict[str, Any] = {}
        if data.get("document_identification") is not None:
            identity_document["documentIdentification"] = data["document_identification"]
        m = build_metadata("type_of_document")
        if m:
            identity_document["typeOfDocument"] = m
        if identity_document:
            result["identityDocument"] = identity_document

        # travel
        travel = pick(data, {"travel_distance_to_work": "travelDistanceToWork"})
        if travel:
            result["travel"] = travel

        # address
        address: Dict[str, Any] = {}
        address.update(pick(data, {
            "street": "street",
            "city": "city",
            "house_number": "houseNumber",
            "house_number_addition": "houseNumberAddition",
            "postal_code": "postalCode",
            "location": "location",
        }))
        m = build_metadata("further_indication")
        if m:
            address["furtherIndication"] = m
        country: Dict[str, Any] = {}
        if data.get("country_key") is not None:
            country["key"] = data["country_key"]
        if data.get("country_value") is not None:
            country["value"] = data["country_value"]
        if data.get("country_iso_code") is not None:
            country["isoCode"] = data["country_iso_code"]
        direct_country = data.get("country")
        if isinstance(direct_country, dict):
            country.update({k: v for k, v in direct_country.items() if v is not None})
        if country:
            address["country"] = country
        if address:
            result["address"] = address

        # deviatingPostalAddress
        dpa: Dict[str, Any] = {}
        dpa.update(pick(data, {
            "deviating_street": "street",
            "deviating_city": "city",
            "deviating_house_number": "houseNumber",
            "deviating_house_number_addition": "houseNumberAddition",
            "deviating_postal_code": "postalCode",
            "deviating_location": "location",
            "deviating_po_box": "poBox",
        }))
        m = build_metadata("deviating_further_indication")
        if m:
            dpa["furtherIndication"] = m
        dpa_country: Dict[str, Any] = {}
        if data.get("deviating_country_key") is not None:
            dpa_country["key"] = data["deviating_country_key"]
        if data.get("deviating_country_value") is not None:
            dpa_country["value"] = data["deviating_country_value"]
        if data.get("deviating_country_iso_code") is not None:
            dpa_country["isoCode"] = data["deviating_country_iso_code"]
        direct_dpa_country = data.get("deviating_country")
        if isinstance(direct_dpa_country, dict):
            dpa_country.update({k: v for k, v in direct_dpa_country.items() if v is not None})
        if dpa_country:
            dpa["country"] = dpa_country
        if dpa:
            result["deviatingPostalAddress"] = dpa

        return result




class EmployeeBsnUpdate(BaseModel):
    """Schema for updating employee BSN (citizen service number)."""
    citizen_service_number: Optional[str] = Field(
        default=None,
        alias="citizenServiceNumber",
        description="The social security number of the employee used in communication with the Dutch tax authorities. The number has to be a valid Dutch citizen service number (BSN).",
        example="123456789",
        min_length=9,
        max_length=9,
        pattern=r"^\d{9}$"
    )

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


# ==================== CREATE EMPLOYEE SCHEMAS ====================

class IdReference(BaseModel):
    """Reference schema with ID field."""
    id: str = Field(..., description="The unique identifier")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class Shift(BaseModel):
    """Shift schema."""
    shift_number: int = Field(..., alias="shiftNumber", description="The shift number")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class CalculateUsingWorkPattern(BaseModel):
    """Calculate using work pattern schema."""
    leave_hours: Optional[bool] = Field(None, alias="leaveHours", description="Calculate leave hours")
    hours_broken_period: Optional[bool] = Field(None, alias="hoursBrokenPeriod", description="Calculate hours broken period")
    hours_period: Optional[bool] = Field(None, alias="hoursPeriod", description="Calculate hours period")
    days_daily_rate: Optional[bool] = Field(None, alias="daysDailyRate", description="Calculate days daily rate")
    deviating_days_and_hours: Optional[bool] = Field(None, alias="deviatingDaysAndHours", description="Calculate deviating days and hours")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class WeekPattern(BaseModel):
    """Week pattern schema."""
    monday: Optional[float] = Field(None, description="Hours on Monday")
    tuesday: Optional[float] = Field(None, description="Hours on Tuesday")
    wednesday: Optional[float] = Field(None, description="Hours on Wednesday")
    thursday: Optional[float] = Field(None, description="Hours on Thursday")
    friday: Optional[float] = Field(None, description="Hours on Friday")
    saturday: Optional[float] = Field(None, description="Hours on Saturday")
    sunday: Optional[float] = Field(None, description="Hours on Sunday")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class WorkPattern(BaseModel):
    """Work pattern schema."""
    odd_weeks: Optional[WeekPattern] = Field(None, alias="oddWeeks", description="Odd weeks pattern")
    even_weeks: Optional[WeekPattern] = Field(None, alias="evenWeeks", description="Even weeks pattern")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class EmploymentData(BaseModel):
    """Employment data nested schema."""
    start_date: Optional[str] = Field(None, alias="startDate", description="The start date of the employment")
    historical_start_date: Optional[str] = Field(None, alias="historicalStartDate", description="The historical start date")
    payroll_administration: Optional[IdReference] = Field(None, alias="payrollAdministration", description="Payroll administration reference")
    non_payroll_administration: Optional[IdReference] = Field(None, alias="nonPayrollAdministration", description="Non-payroll administration reference")
    commission_until_date: Optional[str] = Field(None, alias="commissionUntilDate", description="Commission until date")
    income_relationship_number: Optional[int] = Field(None, alias="incomeRelationshipNumber", description="Income relationship number")
    employee_profile_id: Optional[MetadataWithKey] = Field(None, alias="employeeProfileId", description="Employee profile ID")
    employment_duration_type: Optional[MetadataWithKey] = Field(None, alias="employmentDurationType", description="Employment duration type")
    start_date_contract_of_indefinite_duration: Optional[str] = Field(None, alias="startDateContractOfIndefiniteDuration", description="Start date of contract of indefinite duration")
    employment_contract_type: Optional[MetadataWithKey] = Field(None, alias="employmentContractType", description="Employment contract type")
    type_of_employee: Optional[MetadataWithKey] = Field(None, alias="typeOfEmployee", description="Type of employee")
    cancellation_period_employee: Optional[int] = Field(None, alias="cancellationPeriodEmployee", description="Cancellation period employee")
    cancellation_period_employer: Optional[int] = Field(None, alias="cancellationPeriodEmployer", description="Cancellation period employer")
    cancellation_period_time_unit: Optional[MetadataWithKey] = Field(None, alias="cancellationPeriodTimeUnit", description="Cancellation period time unit")
    cancellation_notice_date: Optional[str] = Field(None, alias="cancellationNoticeDate", description="Cancellation notice date")
    start_cancellation_notice_period: Optional[str] = Field(None, alias="startCancellationNoticePeriod", description="Start cancellation notice period")
    is_director_and_major_shareholder: Optional[bool] = Field(None, alias="isDirectorAndMajorShareholder", description="Is director and major shareholder")
    is_on_call_employment: Optional[bool] = Field(None, alias="isOnCallEmployment", description="Is on call employment")
    has_on_call_appearance_obligation: Optional[bool] = Field(None, alias="hasOnCallAppearanceObligation", description="Has on call appearance obligation")
    vacation_coupons: Optional[MetadataWithKey] = Field(None, alias="vacationCoupons", description="Vacation coupons")
    special_income_ratio: Optional[MetadataWithKey] = Field(None, alias="specialIncomeRatio", description="Special income ratio")
    is_anonymous_employee: Optional[bool] = Field(None, alias="isAnonymousEmployee", description="Is anonymous employee")
    is_previous_owner: Optional[bool] = Field(None, alias="isPreviousOwner", description="Is previous owner")
    is_family_of_owner: Optional[bool] = Field(None, alias="isFamilyOfOwner", description="Is family of owner")
    is_gemoedsbezwaard_national_insurance: Optional[bool] = Field(None, alias="isGemoedsbezwaardNationalInsurance", description="Is gemoedsbezwaard national insurance")
    is_gemoedsbezwaard_employee_insurance: Optional[bool] = Field(None, alias="isGemoedsbezwaardEmployeeInsurance", description="Is gemoedsbezwaard employee insurance")
    name_payslip: Optional[str] = Field(None, alias="namePayslip", description="Name on payslip", max_length=255)
    calculate_working_hours: Optional[bool] = Field(None, alias="calculateWorkingHours", description="Calculate working hours")
    ess_mutation_set: Optional[MetadataWithKey] = Field(None, alias="essMutationSet", description="ESS mutation set")
    exemption_insurance_obligation: Optional[MetadataWithKey] = Field(None, alias="exemptionInsuranceObligation", description="Exemption insurance obligation")
    send_mdv_notification: Optional[bool] = Field(None, alias="sendMdvNotification", description="Send MDV notification")
    period_pay_grade_adjustment: Optional[int] = Field(None, alias="periodPayGradeAdjustment", description="Period pay grade adjustment")
    signal_pay_grade_adjustment: Optional[bool] = Field(None, alias="signalPayGradeAdjustment", description="Signal pay grade adjustment")
    type_of_participation: Optional[MetadataWithKey] = Field(None, alias="typeOfParticipation", description="Type of participation")
    value_of_participation: Optional[MetadataWithKey] = Field(None, alias="valueOfParticipation", description="Value of participation")
    profession_code: Optional[int] = Field(None, alias="professionCode", description="Profession code")
    deviating_cla_tax_return: Optional[int] = Field(None, alias="deviatingCLATaxReturn", description="Deviating CLA tax return")
    participation_55plus_regulation_uwv: Optional[bool] = Field(None, alias="participation55plusRegulationUWV", description="Participation 55+ regulation UWV")
    email_leave_request: Optional[str] = Field(None, alias="emailLeaveRequest", description="Email leave request", max_length=255)
    written_employment_contract: Optional[bool] = Field(None, alias="writtenEmploymentContract", description="Written employment contract")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class WorkingHoursData(BaseModel):
    """Working hours data nested schema."""
    shift: Optional[Shift] = Field(None, description="Shift information")
    deviating_hours_per_week: Optional[float] = Field(None, alias="deviatingHoursPerWeek", description="Deviating hours per week")
    deviating_sv_days_per_period: Optional[float] = Field(None, alias="deviatingSvDaysPerPeriod", description="Deviating SV days per period")
    average_parttime_factor: Optional[float] = Field(None, alias="averageParttimeFactor", description="Average parttime factor")
    regular_work_pattern: Optional[bool] = Field(None, alias="regularWorkPattern", description="Regular work pattern")
    flexible_hours_contract: Optional[MetadataWithKey] = Field(None, alias="flexibleHoursContract", description="Flexible hours contract")
    contract_code: Optional[MetadataWithKey] = Field(None, alias="contractCode", description="Contract code")
    calculate_using_work_pattern: Optional[CalculateUsingWorkPattern] = Field(None, alias="calculateUsingWorkPattern", description="Calculate using work pattern")
    work_pattern: Optional[WorkPattern] = Field(None, alias="workPattern", description="Work pattern")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class WageData(BaseModel):
    """Wage data nested schema."""
    gross_wage: Optional[float] = Field(None, alias="grossWage", description="Gross wage")
    gross_wage_type: Optional[MetadataWithKey] = Field(None, alias="grossWageType", description="Gross wage type")
    net_wage: Optional[float] = Field(None, alias="netWage", description="Net wage")
    net_wage_type: Optional[MetadataWithKey] = Field(None, alias="netWageType", description="Net wage type")
    pay_scale: Optional[MetadataWithKey] = Field(None, alias="payScale", description="Pay scale")
    pay_grade: Optional[MetadataWithKey] = Field(None, alias="payGrade", description="Pay grade")
    apply_pay_grade: Optional[bool] = Field(None, alias="applyPayGrade", description="Apply pay grade")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class OrganizationalEntityData(BaseModel):
    """Organizational entity data nested schema."""
    function: Optional[MetadataWithKey] = Field(None, description="Function")
    deviating_function_group: Optional[str] = Field(None, alias="deviatingFunctionGroup", description="Deviating function group", max_length=10)
    deviating_function_description: Optional[str] = Field(None, alias="deviatingFunctionDescription", description="Deviating function description", max_length=60)
    standard_function: Optional[MetadataWithKey] = Field(None, alias="standardFunction", description="Standard function")
    department: Optional[MetadataWithKey] = Field(None, description="Department")
    distribution_unit: Optional[MetadataWithKey] = Field(None, alias="distributionUnit", description="Distribution unit")
    place_of_employment: Optional[str] = Field(None, alias="placeOfEmployment", description="Place of employment", max_length=60)
    internal_telephone_extension_number: Optional[str] = Field(None, alias="internalTelephoneExtensionNumber", description="Internal telephone extension number", max_length=10)

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class SocialSecurityData(BaseModel):
    """Social security data nested schema."""
    is_insured_for_sickness_benefits_act: Optional[bool] = Field(None, alias="isInsuredForSicknessBenefitsAct", description="Is insured for sickness benefits act")
    is_insured_for_unemployment_insurance_act: Optional[bool] = Field(None, alias="isInsuredForUnemploymentInsuranceAct", description="Is insured for unemployment insurance act")
    is_insured_for_occupational_disability_insurance_act: Optional[bool] = Field(None, alias="isInsuredForOccupationalDisabilityInsuranceAct", description="Is insured for occupational disability insurance act")
    health_care_insurance_act_type: Optional[MetadataWithKey] = Field(None, alias="healthCareInsuranceActType", description="Health care insurance act type")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class FiscalData(BaseModel):
    """Fiscal data nested schema."""
    annual_salary: Optional[float] = Field(None, alias="annualSalary", description="Annual salary")
    deviating_payroll_tax_table_colour: Optional[MetadataWithKey] = Field(None, alias="deviatingPayrollTaxTableColour", description="Deviating payroll tax table colour")
    apply_day_tables: Optional[bool] = Field(None, alias="applyDayTables", description="Apply day tables")
    apply_deviating_payroll_tax_percentage_on: Optional[MetadataWithKey] = Field(None, alias="applyDeviatingPayrollTaxPercentageOn", description="Apply deviating payroll tax percentage on")
    apply_payroll_tax_deduction: Optional[bool] = Field(None, alias="applyPayrollTaxDeduction", description="Apply payroll tax deduction")
    apply_student_deduction: Optional[bool] = Field(None, alias="applyStudentDeduction", description="Apply student deduction")
    deviating_calculation_rule_payroll_tax: Optional[MetadataWithKey] = Field(None, alias="deviatingCalculationRulePayrollTax", description="Deviating calculation rule payroll tax")
    resident_of: Optional[MetadataWithKey] = Field(None, alias="residentOf", description="Resident of")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class OtherPayrollVariablesData(BaseModel):
    """Other payroll variables data nested schema."""
    deviating_premium_group: Optional[MetadataWithKey] = Field(None, alias="deviatingPremiumGroup", description="Deviating premium group")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class CitizenServiceNumber(BaseModel):
    """Citizen service number nested schema."""
    citizen_service_number: Optional[str] = Field(None, alias="citizenServiceNumber", description="Citizen service number", min_length=9, max_length=9, pattern=r"^\d{9}$")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"


class EmployeeData(BaseModel):
    """Employee data nested schema for create."""
    employee_number: int = Field(..., alias="employeeNumber", description="The employee number", ge=1)
    personal_details: PersonalDetails = Field(..., alias="personalDetails", description="Personal details of the employee")
    contact_information: Optional[ContactInformation] = Field(None, alias="contactInformation", description="Contact information of the employee")
    identity_document: Optional[IdentityDocument] = Field(None, alias="identityDocument", description="Identity document of the employee")
    address: Optional[Address] = Field(None, alias="address", description="Address of the employee")
    deviating_postal_address: Optional[DeviatingPostalAddress] = Field(None, alias="deviatingPostalAddress", description="Deviating postal address of the employee")
    iban: Optional[str] = Field(None, description="IBAN of the employee", max_length=34)

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class EmployeeCreate(BaseModel):
    """Schema for creating employee with all required data."""
    employee_data: EmployeeData = Field(..., alias="employeeData", description="Employee data")
    employment_data: EmploymentData = Field(..., alias="employmentData", description="Employment data")
    working_hours_data: Optional[WorkingHoursData] = Field(None, alias="workingHoursData", description="Working hours data")
    wage_data: Optional[WageData] = Field(None, alias="wageData", description="Wage data")
    organizational_entity_data: Optional[OrganizationalEntityData] = Field(None, alias="organizationalEntityData", description="Organizational entity data")
    social_security_data: Optional[SocialSecurityData] = Field(None, alias="socialSecurityData", description="Social security data")
    fiscal_data: Optional[FiscalData] = Field(None, alias="fiscalData", description="Fiscal data")
    other_payroll_variables_data: Optional[OtherPayrollVariablesData] = Field(None, alias="otherPayrollVariablesData", description="Other payroll variables data")
    citizen_service_number: Optional[CitizenServiceNumber] = Field(None, alias="citizenServiceNumber", description="Citizen service number")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert flat input into nested structure expected by EmployeeCreate.
        Handles `_key`, `_value`, `_iso_code`, `_id` suffixes and special groups
        like `calculate_using_work_pattern_*` and `shift_shift_number`.
        """
        if not isinstance(values, dict):
            return values

        # If already properly nested, return as is
        if "employee_data" in values or "employeeData" in values:
            return values

        data = values.copy()

        def pick(source: Dict[str, Any], keys: Dict[str, str]) -> Dict[str, Any]:
            out: Dict[str, Any] = {}
            for src_key, dst_key in keys.items():
                if src_key in source and source[src_key] is not None:
                    out[dst_key] = source[src_key]
            return out

        def build_metadata(src_prefix: str, dst_key: str, container: Dict[str, Any]) -> None:
            key = data.get(f"{src_prefix}_key", None)
            value = data.get(f"{src_prefix}_value", None)
            iso_code = data.get(f"{src_prefix}_iso_code", None)
            # Accept also direct object under src_prefix if present
            direct_obj = data.get(src_prefix, None)
            obj: Dict[str, Any] = {}
            if isinstance(direct_obj, dict):
                obj.update({k: v for k, v in direct_obj.items() if v is not None})
            if key is not None:
                obj["key"] = key
            if value is not None:
                obj["value"] = value
            if iso_code is not None:
                # prefer alias field name used by API
                obj["isoCode"] = iso_code
            if obj:
                container[dst_key] = obj

        def build_id_reference(src_prefix: str, dst_key: str, container: Dict[str, Any]) -> None:
            ref_id = data.get(f"{src_prefix}_id", None)
            if ref_id is not None:
                container[dst_key] = {"id": ref_id}

        processed_keys: set = set()

        # ================== EMPLOYEE DATA ==================
        employee_data: Dict[str, Any] = {}

        # direct
        for k in ["employee_number", "iban"]:
            if k in data and data[k] is not None:
                employee_data[k] = data[k]
                processed_keys.add(k)

        # personal details
        personal_details: Dict[str, Any] = {}
        personal_simple = pick(
            data,
            {
                "first_name": "firstName",
                "last_name": "lastName",
                "prefix": "prefix",
                "initials": "initials",
                "last_name_partner": "lastNamePartner",
                "prefix_partner": "prefixPartner",
                "formatted_name": "formattedName",
                "date_of_birth": "dateOfBirth",
                "place_of_birth": "placeOfBirth",
                "date_of_death": "dateOfDeath",
                "aow_date": "aowDate",
                "photo": "photo",
            },
        )
        if personal_simple:
            personal_details.update(personal_simple)
            processed_keys.update(personal_simple.keys())

        personal_meta_aliases = {
            "how_to_format_last_name": "howToFormatLastName",
            "title": "title",
            "nationality": "nationality",
            "gender": "gender",
            "civil_status": "civilStatus",
        }
        for src_key, dst_key in personal_meta_aliases.items():
            build_metadata(src_key, dst_key, personal_details)
            for suf in ["_key", "_value", "_iso_code"]:
                key_name = f"{src_key}{suf}"
                if key_name in data:
                    processed_keys.add(key_name)

        # contact information
        contact_information = pick(
            data,
            {
                "phone_number": "phoneNumber",
                "mobile_phone_number": "mobilePhoneNumber",
                "fax_number": "faxNumber",
                "email_address": "emailAddress",
                "business_phone_number": "businessPhoneNumber",
                "business_mobile_phone_number": "businessMobilePhoneNumber",
                "business_email_address": "businessEmailAddress",
            },
        )
        processed_keys.update(contact_information.keys())

        # identity document
        identity_document: Dict[str, Any] = {}
        if "document_identification" in data and data["document_identification"] is not None:
            identity_document["documentIdentification"] = data["document_identification"]
            processed_keys.add("document_identification")
        # type_of_document is MetadataWithKey
        build_metadata("type_of_document", "typeOfDocument", identity_document)
        if "type_of_document_key" in data:
            processed_keys.add("type_of_document_key")

        # address
        address: Dict[str, Any] = {}
        addr_simple = pick(
            data,
            {
                "street": "street",
                "city": "city",
                "house_number": "houseNumber",
                "house_number_addition": "houseNumberAddition",
                "postal_code": "postalCode",
                "location": "location",
            },
        )
        if addr_simple:
            address.update(addr_simple)
            processed_keys.update(addr_simple.keys())
        # address.further_indication (MetadataWithKeyAndValue)
        build_metadata("further_indication", "furtherIndication", address)
        for k in ["further_indication_key", "further_indication_value"]:
            if k in data:
                processed_keys.add(k)
        # address.country (CountryWithIsoCode)
        country_obj: Dict[str, Any] = {}
        if data.get("country_key") is not None:
            country_obj["key"] = data["country_key"]
            processed_keys.add("country_key")
        if data.get("country_value") is not None:
            country_obj["value"] = data["country_value"]
            processed_keys.add("country_value")
        if data.get("country_iso_code") is not None:
            country_obj["isoCode"] = data["country_iso_code"]
            processed_keys.add("country_iso_code")
        if country_obj:
            address["country"] = country_obj

        # deviating postal address
        deviating_postal_address: Dict[str, Any] = {}
        dpa_map = {
            "deviating_street": "street",
            "deviating_city": "city",
            "deviating_house_number": "houseNumber",
            "deviating_house_number_addition": "houseNumberAddition",
            "deviating_postal_code": "postalCode",
            "deviating_location": "location",
            "deviating_po_box": "poBox",
        }
        for src_key, dst_key in dpa_map.items():
            if src_key in data and data[src_key] is not None:
                deviating_postal_address[dst_key] = data[src_key]
                processed_keys.add(src_key)
        # deviating further_indication and country
        dpa_country: Dict[str, Any] = {}
        if data.get("deviating_country_key") is not None:
            dpa_country["key"] = data["deviating_country_key"]
            processed_keys.add("deviating_country_key")
        if data.get("deviating_country_value") is not None:
            dpa_country["value"] = data["deviating_country_value"]
            processed_keys.add("deviating_country_value")
        if data.get("deviating_country_iso_code") is not None:
            dpa_country["isoCode"] = data["deviating_country_iso_code"]
            processed_keys.add("deviating_country_iso_code")
        if dpa_country:
            deviating_postal_address["country"] = dpa_country

        dpa_fi: Dict[str, Any] = {}
        if data.get("deviating_further_indication_key") is not None:
            dpa_fi["key"] = data["deviating_further_indication_key"]
            processed_keys.add("deviating_further_indication_key")
        if data.get("deviating_further_indication_value") is not None:
            dpa_fi["value"] = data["deviating_further_indication_value"]
            processed_keys.add("deviating_further_indication_value")
        if dpa_fi:
            deviating_postal_address["furtherIndication"] = dpa_fi

        # ================== EMPLOYMENT DATA ==================
        employment_data: Dict[str, Any] = {}
        employment_simple_alias_map = {
            "start_date": "startDate",
            "historical_start_date": "historicalStartDate",
            "start_date_contract_of_indefinite_duration": "startDateContractOfIndefiniteDuration",
            "commission_until_date": "commissionUntilDate",
            "income_relationship_number": "incomeRelationshipNumber",
            "cancellation_period_employee": "cancellationPeriodEmployee",
            "cancellation_period_employer": "cancellationPeriodEmployer",
            "cancellation_notice_date": "cancellationNoticeDate",
            "start_cancellation_notice_period": "startCancellationNoticePeriod",
            "is_director_and_major_shareholder": "isDirectorAndMajorShareholder",
            "is_on_call_employment": "isOnCallEmployment",
            "has_on_call_appearance_obligation": "hasOnCallAppearanceObligation",
            "is_anonymous_employee": "isAnonymousEmployee",
            "is_previous_owner": "isPreviousOwner",
            "is_family_of_owner": "isFamilyOfOwner",
            "name_payslip": "namePayslip",
            "calculate_working_hours": "calculateWorkingHours",
            "send_mdv_notification": "sendMdvNotification",
            "period_pay_grade_adjustment": "periodPayGradeAdjustment",
            "signal_pay_grade_adjustment": "signalPayGradeAdjustment",
            "deviating_cla_tax_return": "deviatingCLATaxReturn",
            "profession_code": "professionCode",
            "participation_55plus_regulation_uwv": "participation55plusRegulationUWV",
            "email_leave_request": "emailLeaveRequest",
            "written_employment_contract": "writtenEmploymentContract",
            "is_gemoedsbezwaard_national_insurance": "isGemoedsbezwaardNationalInsurance",
            "is_gemoedsbezwaard_employee_insurance": "isGemoedsbezwaardEmployeeInsurance",
        }
        for src_key, dst_key in employment_simple_alias_map.items():
            if src_key in data and data[src_key] is not None:
                employment_data[dst_key] = data[src_key]
                processed_keys.add(src_key)

        # Id references
        id_ref_alias = {
            "payroll_administration": "payrollAdministration",
            "non_payroll_administration": "nonPayrollAdministration",
        }
        for src_key, dst_key in id_ref_alias.items():
            build_id_reference(src_key, dst_key, employment_data)
            if f"{src_key}_id" in data:
                processed_keys.add(f"{src_key}_id")

        # Metadata in employment
        employment_meta_aliases = {
            "employee_profile_id": "employeeProfileId",
            "employment_duration_type": "employmentDurationType",
            "employment_contract_type": "employmentContractType",
            "type_of_employee": "typeOfEmployee",
            "cancellation_period_time_unit": "cancellationPeriodTimeUnit",
            "vacation_coupons": "vacationCoupons",
            "special_income_ratio": "specialIncomeRatio",
            "ess_mutation_set": "essMutationSet",
            "exemption_insurance_obligation": "exemptionInsuranceObligation",
            "type_of_participation": "typeOfParticipation",
            "value_of_participation": "valueOfParticipation",
        }
        for src_key, dst_key in employment_meta_aliases.items():
            build_metadata(src_key, dst_key, employment_data)
            for suf in ["_key", "_value", "_iso_code"]:
                key_name = f"{src_key}{suf}"
                if key_name in data:
                    processed_keys.add(key_name)

        # ================== WORKING HOURS DATA ==================
        working_hours_data: Dict[str, Any] = {}
        wh_simple = pick(
            data,
            {
                "deviating_hours_per_week": "deviatingHoursPerWeek",
                "deviating_sv_days_per_period": "deviatingSvDaysPerPeriod",
                "average_parttime_factor": "averageParttimeFactor",
                "regular_work_pattern": "regularWorkPattern",
            },
        )
        if wh_simple:
            working_hours_data.update(wh_simple)
            processed_keys.update(wh_simple.keys())

        # shift
        if data.get("shift_shift_number") is not None:
            working_hours_data["shift"] = {"shiftNumber": data["shift_shift_number"]}
            processed_keys.add("shift_shift_number")

        # flexible_hours_contract and contract_code as metadata
        for src_key, dst_key in {"flexible_hours_contract": "flexibleHoursContract", "contract_code": "contractCode"}.items():
            build_metadata(src_key, dst_key, working_hours_data)
            if f"{src_key}_key" in data:
                processed_keys.add(f"{src_key}_key")

        # calculateUsingWorkPattern group (use alias keys to match API exactly)
        cwp_keys = {
            "calculate_using_work_pattern_leave_hours": "leaveHours",
            "calculate_using_work_pattern_hours_broken_period": "hoursBrokenPeriod",
            "calculate_using_work_pattern_hours_period": "hoursPeriod",
            "calculate_using_work_pattern_days_daily_rate": "daysDailyRate",
            "calculate_using_work_pattern_deviating_days_and_hours": "deviatingDaysAndHours",
        }
        cwp = pick(data, cwp_keys)
        if cwp:
            working_hours_data["calculateUsingWorkPattern"] = cwp
            processed_keys.update(cwp_keys.keys())
        # Ensure calculate_using_work_pattern object exists if working hours are provided
        need_cwp = (
            bool(wh_simple)
            or data.get("shift_shift_number") is not None
            or any(k in data for k in cwp_keys.keys())
        )
        if need_cwp and "calculateUsingWorkPattern" not in working_hours_data:
            cwp_default: Dict[str, Any] = {}
            for flat_key, dst_key in cwp_keys.items():
                if flat_key in data and data[flat_key] is not None:
                    cwp_default[dst_key] = data[flat_key]
            # Fill missing with explicit False as API requires the object
            for dst_key in [
                "leaveHours",
                "hoursBrokenPeriod",
                "hoursPeriod",
                "daysDailyRate",
                "deviatingDaysAndHours",
            ]:
                cwp_default.setdefault(dst_key, False)
            working_hours_data["calculateUsingWorkPattern"] = cwp_default

        # ================== WAGE DATA ==================
        wage_data: Dict[str, Any] = {}
        wd_simple = pick(
            data,
            {
                "gross_wage": "grossWage",
                "net_wage": "netWage",
                "apply_pay_grade": "applyPayGrade",
            },
        )
        if wd_simple:
            wage_data.update(wd_simple)
            processed_keys.update(wd_simple.keys())
        for src_key, dst_key in {
            "gross_wage_type": "grossWageType",
            "net_wage_type": "netWageType",
            "pay_scale": "payScale",
            "pay_grade": "payGrade",
        }.items():
            build_metadata(src_key, dst_key, wage_data)
            if f"{src_key}_key" in data:
                processed_keys.add(f"{src_key}_key")

        # ================== ORGANIZATIONAL ENTITY DATA ==================
        organizational_entity_data: Dict[str, Any] = {}
        org_simple = pick(
            data,
            {
                "deviating_function_group": "deviatingFunctionGroup",
                "deviating_function_description": "deviatingFunctionDescription",
                "place_of_employment": "placeOfEmployment",
                "internal_telephone_extension_number": "internalTelephoneExtensionNumber",
            },
        )
        if org_simple:
            organizational_entity_data.update(org_simple)
            processed_keys.update(org_simple.keys())
        for src_key, dst_key in {
            "function": "function",
            "standard_function": "standardFunction",
            "department": "department",
            "distribution_unit": "distributionUnit",
        }.items():
            build_metadata(src_key, dst_key, organizational_entity_data)
            if f"{src_key}_key" in data:
                processed_keys.add(f"{src_key}_key")

        # ================== SOCIAL SECURITY DATA ==================
        social_security_data: Dict[str, Any] = {}
        ss_simple = pick(
            data,
            {
                "is_insured_for_sickness_benefits_act": "isInsuredForSicknessBenefitsAct",
                "is_insured_for_unemployment_insurance_act": "isInsuredForUnemploymentInsuranceAct",
                "is_insured_for_occupational_disability_insurance_act": "isInsuredForOccupationalDisabilityInsuranceAct",
            },
        )
        if ss_simple:
            social_security_data.update(ss_simple)
            processed_keys.update(ss_simple.keys())
        build_metadata("health_care_insurance_act_type", "healthCareInsuranceActType", social_security_data)
        if "health_care_insurance_act_type_key" in data:
            processed_keys.add("health_care_insurance_act_type_key")

        # ================== FISCAL DATA ==================
        fiscal_data: Dict[str, Any] = {}
        fiscal_simple = pick(
            data,
            {
                "annual_salary": "annualSalary",
                "apply_day_tables": "applyDayTables",
                "apply_payroll_tax_deduction": "applyPayrollTaxDeduction",
                "apply_student_deduction": "applyStudentDeduction",
            },
        )
        if fiscal_simple:
            fiscal_data.update(fiscal_simple)
            processed_keys.update(fiscal_simple.keys())
        for src_key, dst_key in {
            "deviating_payroll_tax_table_colour": "deviatingPayrollTaxTableColour",
            "apply_deviating_payroll_tax_percentage_on": "applyDeviatingPayrollTaxPercentageOn",
            "deviating_calculation_rule_payroll_tax": "deviatingCalculationRulePayrollTax",
            "resident_of": "residentOf",
        }.items():
            build_metadata(src_key, dst_key, fiscal_data)
            if f"{src_key}_key" in data:
                processed_keys.add(f"{src_key}_key")

        # ================== OTHER PAYROLL VARIABLES ==================
        other_payroll_variables_data: Dict[str, Any] = {}
        build_metadata("deviating_premium_group", "deviatingPremiumGroup", other_payroll_variables_data)
        if "deviating_premium_group_key" in data:
            processed_keys.add("deviating_premium_group_key")

        # ================== CITIZEN SERVICE NUMBER ==================
        citizen_service_number_data: Dict[str, Any] = {}
        if data.get("citizen_service_number") is not None:
            citizen_service_number_data["citizenServiceNumber"] = data["citizen_service_number"]
            processed_keys.add("citizen_service_number")

        # ================== BUILD RESULT ==================
        result: Dict[str, Any] = {}
        if employee_data or personal_details or contact_information or identity_document or address or deviating_postal_address:
            ed: Dict[str, Any] = {}
            if employee_data.get("employee_number") is not None:
                # Use alias key expected by Pydantic model
                ed["employeeNumber"] = employee_data["employee_number"]
            if employee_data.get("iban") is not None:
                ed["iban"] = employee_data["iban"]
        if personal_details:
                ed["personalDetails"] = personal_details
        if contact_information:
                ed["contactInformation"] = contact_information
        if identity_document:
                ed["identityDocument"] = identity_document
        if address:
                ed["address"] = address
        if deviating_postal_address:
                ed["deviatingPostalAddress"] = deviating_postal_address
        if ed:
            result["employeeData"] = ed

        if employment_data:
            result["employmentData"] = employment_data
        if working_hours_data:
            result["workingHoursData"] = working_hours_data
        if wage_data:
            result["wageData"] = wage_data
        if organizational_entity_data:
            result["organizationalEntityData"] = organizational_entity_data
        if social_security_data:
            result["socialSecurityData"] = social_security_data
        if fiscal_data:
            result["fiscalData"] = fiscal_data
        if other_payroll_variables_data:
            result["otherPayrollVariablesData"] = other_payroll_variables_data
        if citizen_service_number_data:
            result["citizenServiceNumber"] = citizen_service_number_data

        # Add any remaining unprocessed keys for forward-compatibility
        for k, v in data.items():
            if k not in processed_keys and v is not None:
                result[k] = v
        return result
