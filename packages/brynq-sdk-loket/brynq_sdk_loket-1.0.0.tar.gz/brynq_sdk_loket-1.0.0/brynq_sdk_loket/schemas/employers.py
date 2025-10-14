from pandera.typing import Series
import pandera as pa
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel, Functions
from ..utils import flat_to_nested_with_metadata
from pydantic import BaseModel, Field, model_validator
from typing import Optional,Dict,Any, Set
from .base import MetadataWithKeyAndValue


class EmployerGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Employer data returned from Loket API.
    An Employer represents a company or organization in the Loket system.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the employer", alias="id")
    employer_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The employer number", alias="employerNumber", nullable=True)
    employer_logo: Series[str] = pa.Field(coerce=True, description="The employer logo URL", alias="employerLogo", nullable=True)
    provider_logo: Series[str] = pa.Field(coerce=True, description="The provider logo URL", alias="providerLogo", nullable=True)
    company_name: Series[str] = pa.Field(coerce=True, description="The company name", alias="companyName")
    chamber_of_commerce_number: Series[str] = pa.Field(coerce=True, description="The chamber of commerce number", alias="chamberOfCommerceNumber", nullable=True)
    sbi_code: Series[str] = pa.Field(coerce=True, description="The SBI code", alias="sbi.sbiCode", nullable=True)
    sbi_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The SBI key", alias="sbi.key", nullable=True)
    sbi_value: Series[str] = pa.Field(coerce=True, description="The SBI value", alias="sbi.value", nullable=True)
    legal_form_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The legal form key", alias="legalForm.key", nullable=True)
    legal_form_value: Series[str] = pa.Field(coerce=True, description="The legal form value", alias="legalForm.value", nullable=True)
    branch: Series[str] = pa.Field(coerce=True, description="The branch information", alias="branch", nullable=True)
    administration_number: Series[str] = pa.Field(coerce=True, description="The administration number", alias="providerSettings.administrationNumber", nullable=True)
    group_code: Series[str] = pa.Field(coerce=True, description="The group code", alias="providerSettings.groupCode", nullable=True)
    parent_employer_for_consolidated_overviews: Series[str] = pa.Field(coerce=True, description="Parent employer for consolidated overviews", alias="providerSettings.parentEmployerForConsolidatedOverviews", nullable=True)
    send_email_when_salary_slip_is_available: Series[bool] = pa.Field(coerce=True, description="Send email when salary slip is available", alias="providerSettings.sendEmailWhenSalarySlipIsAvailable", nullable=True)
    street: Series[str] = pa.Field(coerce=True, description="The street name", alias="address.street", nullable=True)
    city: Series[str] = pa.Field(coerce=True, description="The city name", alias="address.city", nullable=True)
    house_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The house number", alias="address.houseNumber", nullable=True)
    house_number_addition: Series[str] = pa.Field(coerce=True, description="The house number addition", alias="address.houseNumberAddition", nullable=True)
    further_indication_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Further indication key", alias="address.furtherIndication.key", nullable=True)
    further_indication_value: Series[str] = pa.Field(coerce=True, description="Further indication value", alias="address.furtherIndication.value", nullable=True)
    postal_code: Series[str] = pa.Field(coerce=True, description="The postal code", alias="address.postalCode", nullable=True)
    location: Series[str] = pa.Field(coerce=True, description="The location", alias="address.location", nullable=True)
    country_iso_code: Series[str] = pa.Field(coerce=True, description="The country ISO code", alias="address.country.isoCode", nullable=True)
    country_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The country key", alias="address.country.key", nullable=True)
    country_value: Series[str] = pa.Field(coerce=True, description="The country value", alias="address.country.value", nullable=True)
    province: Series[str] = pa.Field(coerce=True, description="The province", alias="address.province", nullable=True)

    # Contact fields
    contact_name: Series[str] = pa.Field(coerce=True, description="Contact name", alias="contact.name", nullable=True)
    contact_phone_number: Series[str] = pa.Field(coerce=True, description="Contact phone number", alias="contact.phoneNumber", nullable=True)
    contact_function: Series[str] = pa.Field(coerce=True, description="Contact function", alias="contact.function", nullable=True)

    # Contact Information fields
    contact_information_email_address: Series[str] = pa.Field(coerce=True, description="Contact information email address", alias="contactInformation.emailAddress", nullable=True)
    contact_information_fax_number: Series[str] = pa.Field(coerce=True, description="Contact information fax number", alias="contactInformation.faxNumber", nullable=True)
    contact_information_phone_number: Series[str] = pa.Field(coerce=True, description="Contact information phone number", alias="contactInformation.phoneNumber", nullable=True)
    contact_information_website: Series[str] = pa.Field(coerce=True, description="Contact information website", alias="contactInformation.website", nullable=True)

    # Deviating Postal Address fields
    deviating_postal_address_street: Series[str] = pa.Field(coerce=True, description="Deviating postal address street", alias="deviatingPostalAddress.street", nullable=True)
    deviating_postal_address_house_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Deviating postal address house number", alias="deviatingPostalAddress.houseNumber", nullable=True)
    deviating_postal_address_house_number_addition: Series[str] = pa.Field(coerce=True, description="Deviating postal address house number addition", alias="deviatingPostalAddress.houseNumberAddition", nullable=True)
    deviating_postal_address_further_indication_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Deviating postal address further indication key", alias="deviatingPostalAddress.furtherIndication.key", nullable=True)
    deviating_postal_address_further_indication_value: Series[str] = pa.Field(coerce=True, description="Deviating postal address further indication value", alias="deviatingPostalAddress.furtherIndication.value", nullable=True)
    deviating_postal_address_postal_code: Series[str] = pa.Field(coerce=True, description="Deviating postal address postal code", alias="deviatingPostalAddress.postalCode", nullable=True)
    deviating_postal_address_city: Series[str] = pa.Field(coerce=True, description="Deviating postal address city", alias="deviatingPostalAddress.city", nullable=True)
    deviating_postal_address_location: Series[str] = pa.Field(coerce=True, description="Deviating postal address location", alias="deviatingPostalAddress.location", nullable=True)
    deviating_postal_address_country_iso_code: Series[str] = pa.Field(coerce=True, description="Deviating postal address country ISO code", alias="deviatingPostalAddress.country.isoCode", nullable=True)
    deviating_postal_address_country_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Deviating postal address country key", alias="deviatingPostalAddress.country.key", nullable=True)
    deviating_postal_address_country_value: Series[str] = pa.Field(coerce=True, description="Deviating postal address country value", alias="deviatingPostalAddress.country.value", nullable=True)
    deviating_postal_address_po_box: Series[str] = pa.Field(coerce=True, description="Deviating postal address PO box", alias="deviatingPostalAddress.poBox", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False


class EmployerMinimizedGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating minimized Employer data returned from Loket API.
    A minimized Employer represents a simplified version of company data.
    """
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the employer", alias="id")
    employer_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The employer number", alias="employerNumber", nullable=True)
    employer_logo: Series[str] = pa.Field(coerce=True, description="The employer logo URL", alias="employerLogo", nullable=True)
    provider_logo: Series[str] = pa.Field(coerce=True, description="The provider logo URL", alias="providerLogo", nullable=True)
    company_name: Series[str] = pa.Field(coerce=True, description="The company name", alias="companyName")
    branch: Series[str] = pa.Field(coerce=True, description="The branch information", alias="branch", nullable=True)
    administration_number: Series[str] = pa.Field(coerce=True, description="The administration number", alias="providerSettings.administrationNumber", nullable=True)
    group_code: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The group code", alias="providerSettings.groupCode", nullable=True)
    street: Series[str] = pa.Field(coerce=True, description="The street name", alias="address.street", nullable=True)
    city: Series[str] = pa.Field(coerce=True, description="The city name", alias="address.city", nullable=True)
    house_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The house number", alias="address.houseNumber", nullable=True)
    postal_code: Series[str] = pa.Field(coerce=True, description="The postal code", alias="address.postalCode", nullable=True)
    contact_name: Series[str] = pa.Field(coerce=True, description="The contact name", alias="contact.name", nullable=True)
    contact_phone_number: Series[str] = pa.Field(coerce=True, description="The contact phone number", alias="contact.phoneNumber", nullable=True)
    contact_information_phone_number: Series[str] = pa.Field(coerce=True, description="The contact information phone number", alias="contactInformation.phoneNumber", nullable=True)

    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False


# Pydantic schemas for Employer operations
# MetadataWithKeyAndValue is now imported from base.py as MetadataWithKeyAndValue


# Prefix → target alias (nested object name)
# For employers, we directly use snake_case field names as keys, and rely on
# nested field prefixes (e.g., "address", "deviating_postal_address")
PREFIX_MAP: Dict[str, str] = {
    "address": "address",
    "deviating_postal_address": "deviatingPostalAddress",
    "provider_settings": "providerSettings",
    "contact": "contact",
    "contact_information": "contactInformation",
}

# Root level fields expecting MetadataWithKeyAndValue (snake_case)
ROOT_METADATA_FIELDS: Set[str] = {
    "sbi",
    "legal_form",
    "branch",
}

# Nested level fields expecting MetadataWithKeyAndValue (prefix → field set)
NESTED_METADATA_FIELDS: Dict[str, Set[str]] = {
    "address": {"further_indication", "country", "province"},
    "deviating_postal_address": {"further_indication", "country"},
}

class Contact(BaseModel):
    """Contact information for the employer"""
    name: Optional[str] = Field(None, max_length=50, description="Name of the contact of the employer")
    phone_number: Optional[str] = Field(None, max_length=15, alias="phoneNumber", description="The general phone number of the employer")
    function: Optional[str] = Field(None, max_length=50, description="The job title/function of the contact of the employer")


class ContactInformation(BaseModel):
    """Contact information details for the employer"""
    email_address: Optional[str] = Field(None, max_length=255, alias="emailAddress", description="The email address of the employer")
    fax_number: Optional[str] = Field(None, max_length=15, alias="faxNumber", description="The fax number of the employer")
    phone_number: Optional[str] = Field(None, max_length=15, alias="phoneNumber", description="The telephone number of the employer")
    website: Optional[str] = Field(None, max_length=255, description="The website of the employer")


class Address(BaseModel):
    """Address information for the employer"""
    street: Optional[str] = Field(None, max_length=24, description="Streetname of the address")
    city: Optional[str] = Field(None, max_length=24, description="City of the address")
    house_number: Optional[int] = Field(None, alias="houseNumber", description="House number of the address")
    house_number_addition: Optional[str] = Field(None, max_length=4, alias="houseNumberAddition", description="An addition to further specify the house/door/postbox")
    further_indication: Optional[MetadataWithKeyAndValue] = Field(None, alias="furtherIndication", description="Further indication for the address")
    postal_code: Optional[str] = Field(None, max_length=9, alias="postalCode", description="The postal code of the address")
    location: Optional[str] = Field(None, max_length=35, description="The location to further specify the address")
    country: Optional[MetadataWithKeyAndValue] = Field(None, description="Country information")
    province: Optional[MetadataWithKeyAndValue] = Field(None, description="A Dutch province")


class AddressCreate(BaseModel):
    """Address information for the employer - Create version with mandatory fields"""
    street: str = Field(..., max_length=24, description="Streetname of the address (mandatory for create)")
    city: str = Field(..., max_length=24, description="City of the address (mandatory for create)")
    house_number: int = Field(..., alias="houseNumber", description="House number of the address (mandatory for create)")
    house_number_addition: Optional[str] = Field(None, max_length=4, alias="houseNumberAddition", description="An addition to further specify the house/door/postbox")
    further_indication: Optional[MetadataWithKeyAndValue] = Field(None, alias="furtherIndication", description="Further indication for the address")
    postal_code: str = Field(..., max_length=9, alias="postalCode", description="The postal code of the address (mandatory for create)")
    location: Optional[str] = Field(None, max_length=35, description="The location to further specify the address")
    country: MetadataWithKeyAndValue = Field(..., description="Country information (mandatory for create)")
    province: Optional[MetadataWithKeyAndValue] = Field(None, description="A Dutch province")


class DeviatingPostalAddress(BaseModel):
    """Deviating postal address for the employer"""
    street: Optional[str] = Field(None, max_length=24, description="Streetname of the address")
    city: Optional[str] = Field(None, max_length=24, description="City of the address")
    house_number: Optional[int] = Field(None, alias="houseNumber", description="House number of the address")
    house_number_addition: Optional[str] = Field(None, max_length=4, alias="houseNumberAddition", description="An addition to further specify the house/door/postbox")
    further_indication: Optional[MetadataWithKeyAndValue] = Field(None, alias="furtherIndication", description="Further indication for the address")
    postal_code: Optional[str] = Field(None, max_length=9, alias="postalCode", description="The postal code of the address")
    location: Optional[str] = Field(None, max_length=35, description="The location to further specify the address")
    country: Optional[MetadataWithKeyAndValue] = Field(None, description="Country information")
    po_box: Optional[int] = Field(None, alias="poBox", description="Post office box")


class DeviatingPostalAddressCreate(BaseModel):
    """Deviating postal address for the employer - Create version with mandatory fields"""
    street: Optional[str] = Field(None, max_length=24, description="Streetname of the address")
    city: str = Field(..., max_length=24, description="City of the address (mandatory for create)")
    house_number: Optional[int] = Field(None, alias="houseNumber", description="House number of the address")
    house_number_addition: Optional[str] = Field(None, max_length=4, alias="houseNumberAddition", description="An addition to further specify the house/door/postbox")
    further_indication: Optional[MetadataWithKeyAndValue] = Field(None, alias="furtherIndication", description="Further indication for the address")
    postal_code: str = Field(..., max_length=9, alias="postalCode", description="The postal code of the address (mandatory for create)")
    location: Optional[str] = Field(None, max_length=35, description="The location to further specify the address")
    country: MetadataWithKeyAndValue = Field(..., description="Country information (mandatory for create)")
    po_box: Optional[int] = Field(None, alias="poBox", description="Post office box")


class ProviderSettings(BaseModel):
    """Provider settings for the employer"""
    administration_number: Optional[str] = Field(None, max_length=15, alias="administrationNumber", description="A free field that is most commonly used to store the Debtors Number")
    group_code: Optional[int] = Field(None, alias="groupCode", description="The groupcode is used for grouping employers")
    parent_employer_for_consolidated_overviews: Optional[int] = Field(None, alias="parentEmployerForConsolidatedOverviews", description="This field is used to link employers in order to generate reports")
    send_email_when_salary_slip_is_available: Optional[bool] = Field(None, alias="sendEmailWhenSalarySlipIsAvailable", description="Indicates whether an e-mail should be sent to an employee if a salary slip becomes available")


class ProviderSettingsCreate(BaseModel):
    """Provider settings for the employer - Create version with mandatory fields"""
    administration_number: Optional[str] = Field(None, max_length=15, alias="administrationNumber", description="A free field that is most commonly used to store the Debtors Number")
    group_code: Optional[int] = Field(None, alias="groupCode", description="The groupcode is used for grouping employers")
    parent_employer_for_consolidated_overviews: Optional[int] = Field(None, alias="parentEmployerForConsolidatedOverviews", description="This field is used to link employers in order to generate reports")
    send_email_when_salary_slip_is_available: bool = Field(..., alias="sendEmailWhenSalarySlipIsAvailable", description="Indicates whether an e-mail should be sent to an employee if a salary slip becomes available (mandatory for create)")


class EmployerUpdate(BaseModel):
    """Schema for updating employer information"""
    company_name: Optional[str] = Field(None, max_length=70, alias="companyName", example="Acme Corporation")
    chamber_of_commerce_number: Optional[str] = Field(None, max_length=35, alias="chamberOfCommerceNumber", example="12345678")
    sbi: Optional[MetadataWithKeyAndValue] = Field(None)
    legal_form: Optional[MetadataWithKeyAndValue] = Field(None, alias="legalForm")
    branch: Optional[MetadataWithKeyAndValue] = Field(None)

    provider_settings: Optional[ProviderSettings] = Field(None, alias="providerSettings")
    contact: Optional[Contact] = Field(None)
    contact_information: Optional[ContactInformation] = Field(None, alias="contactInformation")
    address: Optional[Address] = Field(None)
    deviating_postal_address: Optional[DeviatingPostalAddress] = Field(None, alias="deviatingPostalAddress")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(values, Dict):
            return values
        # Normalize unprefixed flat keys into expected prefixed form
        v = dict(values)
        normalized: Dict[str, Any] = {}
        address_keys = {
            "street", "city", "house_number", "house_number_addition",
            "further_indication", "postal_code", "location",
            "country", "country_key", "country_iso_code", "country_value",
            "province", "province_key", "province_value"
        }
        for k, val in list(v.items()):
            if k in address_keys:
                normalized[f"address_{k}"] = val
            elif k.startswith("deviating_"):
                # Map deviating_* → deviating_postal_address_*
                suffix = k[len("deviating_"):]
                normalized[f"deviating_postal_address_{suffix}"] = val
            elif k in {"name", "phone_number", "function"}:
                # Contact fields
                normalized[f"contact_{k}"] = val
            elif k == "phone_number_contact_information":
                # Explicit contact information phone number
                normalized["contact_information_phone_number"] = val
            elif k in {"email_address", "fax_number", "website"}:
                # Contact information fields
                normalized[f"contact_information_{k}"] = val
            elif k.startswith("provider_settings_"):
                normalized[k] = val
            elif k in {"send_email_when_salary_slip_is_available", "administration_number", "group_code", "parent_employer_for_consolidated_overviews"}:
                normalized[f"provider_settings_{k}"] = val
            else:
                normalized[k] = val

        return flat_to_nested_with_metadata(
            values=normalized,
            prefix_map=PREFIX_MAP,
            root_metadata_fields=ROOT_METADATA_FIELDS,
            nested_metadata_fields=NESTED_METADATA_FIELDS
        )


class EmployerCreate(BaseModel):
    """Schema for creating employer information"""
    post_model: str = Field(..., alias="postModel", description="The post model field (mandatory for create)", example="standard")
    company_name: str = Field(..., max_length=70, alias="companyName", description="Name of the company (mandatory for create)", example="Acme Corporation")
    chamber_of_commerce_number: Optional[str] = Field(None, max_length=35, alias="chamberOfCommerceNumber", description="Chamber of commerce number", example="12345678")
    sbi: Optional[MetadataWithKeyAndValue] = Field(None, description="The Standard Industrial Classifications")
    legal_form: Optional[MetadataWithKeyAndValue] = Field(None, alias="legalForm", description="Legal form of the company")
    branch: Optional[MetadataWithKeyAndValue] = Field(None, description="Branch information")
    provider_settings: Optional[ProviderSettingsCreate] = Field(None, alias="providerSettings", description="Provider settings for the employer")
    contact: Optional[Contact] = Field(None, description="Contact information for the employer")
    contact_information: Optional[ContactInformation] = Field(None, alias="contactInformation", description="Contact information details")
    address: Optional[AddressCreate] = Field(None, description="Address information for the employer")
    deviating_postal_address: Optional[DeviatingPostalAddressCreate] = Field(None, alias="deviatingPostalAddress", description="Deviating postal address with mandatory fields")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"

    @model_validator(mode="before")
    @classmethod
    def flat_to_nested(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(values, Dict):
            return values
        # Normalize unprefixed flat keys into expected prefixed form
        v = dict(values)
        normalized: Dict[str, Any] = {}
        address_keys = {
            "street", "city", "house_number", "house_number_addition",
            "further_indication", "postal_code", "location",
            "country", "country_key", "country_iso_code", "country_value",
            "province", "province_key", "province_value"
        }
        for k, val in list(v.items()):
            if k in address_keys:
                normalized[f"address_{k}"] = val
            elif k.startswith("deviating_"):
                # Map deviating_* → deviating_postal_address_*
                suffix = k[len("deviating_"):]
                normalized[f"deviating_postal_address_{suffix}"] = val
            elif k in {"name", "phone_number", "function"}:
                # Contact fields
                normalized[f"contact_{k}"] = val
            elif k == "phone_number_contact_information":
                # Explicit contact information phone number
                normalized["contact_information_phone_number"] = val
            elif k in {"email_address", "fax_number", "website"}:
                # Contact information fields
                normalized[f"contact_information_{k}"] = val
            elif k.startswith("provider_settings_"):
                normalized[k] = val
            elif k in {"send_email_when_salary_slip_is_available", "administration_number", "group_code", "parent_employer_for_consolidated_overviews"}:
                normalized[f"provider_settings_{k}"] = val
            else:
                normalized[k] = val

        return flat_to_nested_with_metadata(
            values=normalized,
            prefix_map=PREFIX_MAP,
            root_metadata_fields=ROOT_METADATA_FIELDS,
            nested_metadata_fields=NESTED_METADATA_FIELDS
        )
