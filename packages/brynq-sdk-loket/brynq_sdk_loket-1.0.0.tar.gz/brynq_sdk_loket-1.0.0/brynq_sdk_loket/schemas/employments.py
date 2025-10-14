from pandera.typing import Series
import pandera as pa
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from pydantic import BaseModel, Field
from typing import Optional
from .base import MetadataWithKey, MetadataWithKeyAndValue


class EmploymentGet(BrynQPanderaDataFrameModel):
    """
    Schema for validating Employment data returned from Loket API.
    An Employment represents an employment relationship between an employee and employer.
    """
    # Main employment fields
    id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the employment", alias="id")
    start_date: Series[str] = pa.Field(coerce=True, description="The start date of the employment", alias="startDate")
    end_date: Series[str] = pa.Field(coerce=True, description="The end date of the employment", alias="endDate", nullable=True)
    payroll_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The payroll ID", alias="payrollId")

    # Employee nested fields
    employee_id: Series[str] = pa.Field(coerce=True, description="The unique identifier of the employee", alias="employee.id")
    employee_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The employee number", alias="employee.employeeNumber")
    employee_first_name: Series[str] = pa.Field(coerce=True, description="The first name of the employee", alias="employee.firstName")
    employee_initials: Series[str] = pa.Field(coerce=True, description="The initials of the employee", alias="employee.initials")
    employee_prefix: Series[str] = pa.Field(coerce=True, description="The prefix of the employee", alias="employee.prefix", nullable=True)
    employee_last_name: Series[str] = pa.Field(coerce=True, description="The last name of the employee", alias="employee.lastName")
    employee_formatted_name: Series[str] = pa.Field(coerce=True, description="The formatted name of the employee", alias="employee.formattedName")
    employee_date_of_birth: Series[str] = pa.Field(coerce=True, description="The date of birth of the employee", alias="employee.dateOfBirth")

    # Administration nested fields
    administration_id: Series[str] = pa.Field(coerce=True, description="The administration ID", alias="administration.id")
    administration_name: Series[str] = pa.Field(coerce=True, description="The administration name", alias="administration.name")
    administration_description: Series[str] = pa.Field(coerce=True, description="The administration description", alias="administration.description")
    administration_client_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The administration client number", alias="administration.clientNumber")
    administration_type: Series[str] = pa.Field(coerce=True, description="The administration type", alias="administration.administrationType")

    # Payroll Administration nested fields
    payroll_admin_id: Series[str] = pa.Field(coerce=True, description="The payroll administration ID", alias="payrollAdministration.id", nullable=True)
    payroll_admin_name: Series[str] = pa.Field(coerce=True, description="The payroll administration name", alias="payrollAdministration.name", nullable=True)
    payroll_admin_description: Series[str] = pa.Field(coerce=True, description="The payroll administration description", alias="payrollAdministration.description", nullable=True)
    payroll_admin_client_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The payroll administration client number", alias="payrollAdministration.clientNumber", nullable=True)
    payroll_admin_cla_value: Series[str] = pa.Field(coerce=True, description="The CLA value", alias="payrollAdministration.cla.value", nullable=True)
    payroll_admin_wage_model_value: Series[str] = pa.Field(coerce=True, description="The wage model value", alias="payrollAdministration.wageModel.value", nullable=True)

    # Non-Payroll Administration nested fields (nullable - may not exist in DataFrame when parent is null)
    non_payroll_admin_id: Series[str] = pa.Field(coerce=True, description="The non-payroll administration ID", alias="nonPayrollAdministration.id", nullable=True)
    non_payroll_admin_name: Series[str] = pa.Field(coerce=True, description="The non-payroll administration name", alias="nonPayrollAdministration.name", nullable=True)
    non_payroll_admin_description: Series[str] = pa.Field(coerce=True, description="The non-payroll administration description", alias="nonPayrollAdministration.description", nullable=True)

    # Employment category and type fields
    employment_category_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The employment category type key", alias="employmentCategoryType.key", nullable=True)
    employment_category_type_value: Series[str] = pa.Field(coerce=True, description="The employment category type value", alias="employmentCategoryType.value", nullable=True)
    type_of_employee_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The type of employee key", alias="typeOfEmployee.key", nullable=True)
    type_of_employee_value: Series[str] = pa.Field(coerce=True, description="The type of employee value", alias="typeOfEmployee.value", nullable=True)
    employment_duration_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The employment duration type key", alias="employmentDurationType.key", nullable=True)
    employment_duration_type_value: Series[str] = pa.Field(coerce=True, description="The employment duration type value", alias="employmentDurationType.value", nullable=True)
    employment_contract_type_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The employment contract type key", alias="employmentContractType.key", nullable=True)
    employment_contract_type_value: Series[str] = pa.Field(coerce=True, description="The employment contract type value", alias="employmentContractType.value", nullable=True)

    # Contract dates
    start_date_contract_indefinite_duration: Series[str] = pa.Field(coerce=True, description="The start date of contract of indefinite duration", alias="startDateContractOfIndefiniteDuration", nullable=True)
    historical_start_date: Series[str] = pa.Field(coerce=True, description="The historical start date", alias="historicalStartDate", nullable=True)

    # Additional employee fields that come in original format
    employee_last_name_partner: Series[str] = pa.Field(coerce=True, description="The last name partner of the employee", alias="employee.lastNamePartner", nullable=True)
    employee_prefix_partner: Series[str] = pa.Field(coerce=True, description="The prefix partner of the employee", alias="employee.prefixPartner", nullable=True)
    employee_photo: Series[str] = pa.Field(coerce=True, description="The photo of the employee", alias="employee.photo", nullable=True)

    # Fields that come in original camelCase format (not converted by pd.json_normalize)
    end_of_employment_reason: Series[str] = pa.Field(coerce=True, description="End of employment reason", alias="endOfEmploymentReason", nullable=True)
    end_of_employment_reason_tax_authorities: Series[str] = pa.Field(coerce=True, description="End of employment reason tax authorities", alias="endOfEmploymentReasonTaxAuthorities", nullable=True)
    end_of_employment_due_to_illness: Series[str] = pa.Field(coerce=True, description="End of employment due to illness", alias="endOfEmploymentDueToIllness", nullable=True)
    non_payroll_administration: Series[str] = pa.Field(coerce=True, description="Non payroll administration", alias="nonPayrollAdministration", nullable=True)
    linked_employment: Series[str] = pa.Field(coerce=True, description="Linked employment", alias="linkedEmployment", nullable=True)
    commission_until_date: Series[str] = pa.Field(coerce=True, description="Commission until date", alias="commissionUntilDate", nullable=True)
    commission_until_date1: Series[str] = pa.Field(coerce=True, description="Commission until date 1", alias="commissionUntilDate1", nullable=True)
    commission_until_date2: Series[str] = pa.Field(coerce=True, description="Commission until date 2", alias="commissionUntilDate2", nullable=True)
    commission_until_date3: Series[str] = pa.Field(coerce=True, description="Commission until date 3", alias="commissionUntilDate3", nullable=True)
    commission_until_date4: Series[str] = pa.Field(coerce=True, description="Commission until date 4", alias="commissionUntilDate4", nullable=True)
    commission_until_date5: Series[str] = pa.Field(coerce=True, description="Commission until date 5", alias="commissionUntilDate5", nullable=True)
    commission_until_date6: Series[str] = pa.Field(coerce=True, description="Commission until date 6", alias="commissionUntilDate6", nullable=True)
    vacation_coupons: Series[str] = pa.Field(coerce=True, description="Vacation coupons", alias="vacationCoupons", nullable=True)
    deviating_cla_external_party: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Deviating CLA external party", alias="deviatingCLAExternalParty", nullable=True)
    deviating_cla_tax_return: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Deviating CLA tax return", alias="deviatingCLATaxReturn", nullable=True)
    profession_code: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Profession code", alias="professionCode", nullable=True)
    email_leave_request: Series[str] = pa.Field(coerce=True, description="Email leave request", alias="emailLeaveRequest", nullable=True)
    period_pay_grade_adjustment: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Period pay grade adjustment", alias="periodPayGradeAdjustment", nullable=True)
    has_on_call_appearance_obligation: Series[bool] = pa.Field(coerce=True, description="Has on call appearance obligation", alias="hasOnCallAppearanceObligation", nullable=True)
    cancellation_period_employee: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Cancellation period employee", alias="cancellationPeriodEmployee", nullable=True)
    cancellation_period_employer: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Cancellation period employer", alias="cancellationPeriodEmployer", nullable=True)
    cancellation_notice_date: Series[str] = pa.Field(coerce=True, description="Cancellation notice date", alias="cancellationNoticeDate", nullable=True)
    start_cancellation_notice_period: Series[str] = pa.Field(coerce=True, description="Start cancellation notice period", alias="startCancellationNoticePeriod", nullable=True)
    name_payslip: Series[str] = pa.Field(coerce=True, description="Name payslip", alias="namePayslip", nullable=True)

    # Employment flags and settings
    first_day_notification: Series[bool] = pa.Field(coerce=True, description="First day notification flag", alias="firstDayNotification", nullable=True)
    income_relationship_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The income relationship number", alias="incomeRelationshipNumber", nullable=True)
    exemption_work_related_expense_scheme: Series[bool] = pa.Field(coerce=True, description="Exemption work related expense scheme", alias="exemptionWorkRelatedExpenseScheme", nullable=True)
    exemption_premium_waiver_marginal_labour: Series[bool] = pa.Field(coerce=True, description="Exemption premium waiver marginal labour", alias="exemptionPremiumWaiverMarginalLabour", nullable=True)
    wachtgeld_old_regulation: Series[bool] = pa.Field(coerce=True, description="Wachtgeld old regulation", alias="wachtgeldOldRegulation", nullable=True)
    participation_55plus_regulation_uwv: Series[bool] = pa.Field(coerce=True, description="Participation 55+ regulation UWV", alias="participation55plusRegulationUWV", nullable=True)

    # Director and ownership flags
    is_director_and_major_shareholder: Series[bool] = pa.Field(coerce=True, description="Is director and major shareholder", alias="isDirectorAndMajorShareholder", nullable=True)
    is_previous_owner: Series[bool] = pa.Field(coerce=True, description="Is previous owner", alias="isPreviousOwner", nullable=True)
    is_family_of_owner: Series[bool] = pa.Field(coerce=True, description="Is family of owner", alias="isFamilyOfOwner", nullable=True)
    is_on_call_employment: Series[bool] = pa.Field(coerce=True, description="Is on call employment", alias="isOnCallEmployment", nullable=True)

    # Insurance and tax flags
    is_gemoedsbezwaard_national_insurance: Series[bool] = pa.Field(coerce=True, description="Is gemoedsbezwaard national insurance", alias="isGemoedsbezwaardNationalInsurance", nullable=True)
    is_gemoedsbezwaard_employee_insurance: Series[bool] = pa.Field(coerce=True, description="Is gemoedsbezwaard employee insurance", alias="isGemoedsbezwaardEmployeeInsurance", nullable=True)
    is_anonymous_employee: Series[bool] = pa.Field(coerce=True, description="Is anonymous employee", alias="isAnonymousEmployee", nullable=True)

    # Contract settings
    calculate_working_hours: Series[bool] = pa.Field(coerce=True, description="Calculate working hours", alias="calculateWorkingHours", nullable=True)
    written_employment_contract: Series[bool] = pa.Field(coerce=True, description="Written employment contract", alias="writtenEmploymentContract", nullable=True)
    signal_pay_grade_adjustment: Series[bool] = pa.Field(coerce=True, description="Signal pay grade adjustment", alias="signalPayGradeAdjustment", nullable=True)

    # Metadata object fields (key-value pairs)
    employee_profile_id_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="The employee profile ID key", alias="employeeProfileId.key", nullable=True)
    employee_profile_id_value: Series[str] = pa.Field(coerce=True, description="The employee profile ID value", alias="employeeProfileId.value", nullable=True)
    send_to_external_party_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Send to external party key", alias="sendToExternalParty.key", nullable=True)
    send_to_external_party_value: Series[str] = pa.Field(coerce=True, description="Send to external party value", alias="sendToExternalParty.value", nullable=True)
    exemption_insurance_obligation_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Exemption insurance obligation key", alias="exemptionInsuranceObligation.key", nullable=True)
    exemption_insurance_obligation_value: Series[str] = pa.Field(coerce=True, description="Exemption insurance obligation value", alias="exemptionInsuranceObligation.value", nullable=True)
    temporary_tax_exemption_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Temporary tax exemption key", alias="temporaryTaxExemption.key", nullable=True)
    temporary_tax_exemption_value: Series[str] = pa.Field(coerce=True, description="Temporary tax exemption value", alias="temporaryTaxExemption.value", nullable=True)
    cancellation_period_time_unit_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Cancellation period time unit key", alias="cancellationPeriodTimeUnit.key", nullable=True)
    cancellation_period_time_unit_value: Series[str] = pa.Field(coerce=True, description="Cancellation period time unit value", alias="cancellationPeriodTimeUnit.value", nullable=True)
    ess_mutation_set_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="ESS mutation set key", alias="essMutationSet.key", nullable=True)
    ess_mutation_set_value: Series[str] = pa.Field(coerce=True, description="ESS mutation set value", alias="essMutationSet.value", nullable=True)

    # Additional metadata objects from API spec (nullable - may not exist in DataFrame when parent objects are null)
    end_of_employment_reason_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="End of employment reason key", alias="endOfEmploymentReason.key", nullable=True)
    end_of_employment_reason_value: Series[str] = pa.Field(coerce=True, description="End of employment reason value", alias="endOfEmploymentReason.value", nullable=True)
    end_of_employment_reason_tax_authorities_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="End of employment reason tax authorities key", alias="endOfEmploymentReasonTaxAuthorities.key", nullable=True)
    end_of_employment_reason_tax_authorities_value: Series[str] = pa.Field(coerce=True, description="End of employment reason tax authorities value", alias="endOfEmploymentReasonTaxAuthorities.value", nullable=True)
    vacation_coupons_key: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Vacation coupons key", alias="vacationCoupons.key", nullable=True)
    vacation_coupons_value: Series[str] = pa.Field(coerce=True, description="Vacation coupons value", alias="vacationCoupons.value", nullable=True)
    type_of_participation: Series[object] = pa.Field(coerce=True, description="Type of participation", alias="typeOfParticipation", nullable=True)
    value_of_participation: Series[object] = pa.Field(coerce=True, description="Value of participation", alias="valueOfParticipation", nullable=True)
    special_income_ratio: Series[object] = pa.Field(coerce=True, description="Special income ratio", alias="specialIncomeRatio", nullable=True)


    class _Annotation:
        primary_key = "id"

    class Config:
        coerce = True
        strict = False
        add_missing_columns = True




class EmploymentUpdate(BaseModel):
    """Payload schema for updating employment details."""
    historical_start_date: Optional[str] = Field(None, alias="historicalStartDate", description="Historical employment start date", example="2020-01-01")
    commission_until_date: Optional[str] = Field(None, alias="commissionUntilDate", description="Employment end date", example="2024-12-31")
    commission_until_date1: Optional[str] = Field(None, alias="commissionUntilDate1", description="Commission until date #1", example="2024-12-31")
    commission_until_date2: Optional[str] = Field(None, alias="commissionUntilDate2", description="Commission until date #2", example="2024-12-31")
    commission_until_date3: Optional[str] = Field(None, alias="commissionUntilDate3", description="Commission until date #3", example="2024-12-31")
    commission_until_date4: Optional[str] = Field(None, alias="commissionUntilDate4", description="Commission until date #4", example="2024-12-31")
    commission_until_date5: Optional[str] = Field(None, alias="commissionUntilDate5", description="Commission until date #5", example="2024-12-31")
    commission_until_date6: Optional[str] = Field(None, alias="commissionUntilDate6", description="Commission until date #6", example="2024-12-31")
    type_of_employee: Optional[MetadataWithKey] = Field(None, alias="typeOfEmployee", description="Employee type metadata")
    employment_duration_type: Optional[MetadataWithKey] = Field(None, alias="employmentDurationType", description="Employment duration type metadata")
    start_date_contract_of_indefinite_duration: Optional[str] = Field(None, alias="startDateContractOfIndefiniteDuration", description="Start date for indefinite contract", example="2024-01-01")
    employment_contract_type: Optional[MetadataWithKey] = Field(None, alias="employmentContractType", description="Employment contract type metadata")
    vacation_coupons: Optional[MetadataWithKey] = Field(None, alias="vacationCoupons", description="Vacation coupons metadata")
    send_to_external_party: Optional[MetadataWithKey] = Field(None, alias="sendToExternalParty", description="External party delivery metadata")
    deviating_cla_external_party: Optional[int] = Field(None, alias="deviatingCLAExternalParty", description="Deviating CLA for external parties", ge=0)
    deviating_cla_tax_return: Optional[int] = Field(None, alias="deviatingCLATaxReturn", description="Deviating CLA for tax returns", ge=1, le=9999)
    income_relationship_number: Optional[int] = Field(None, alias="incomeRelationshipNumber", description="Income relationship number", ge=0, le=9999)
    employee_profile_id: Optional[MetadataWithKey] = Field(None, alias="employeeProfileId", description="Employee profile metadata")
    profession_code: Optional[int] = Field(None, alias="professionCode", description="Profession code", ge=1, le=999)
    exemption_work_related_expense_scheme: Optional[bool] = Field(None, alias="exemptionWorkRelatedExpenseScheme", description="Work-related expense scheme exemption flag")
    exemption_premium_waiver_marginal_labour: Optional[bool] = Field(None, alias="exemptionPremiumWaiverMarginalLabour", description="Premium waiver marginal labour exemption flag")
    type_of_participation: Optional[MetadataWithKey] = Field(None, alias="typeOfParticipation", description="Participation type metadata")
    value_of_participation: Optional[MetadataWithKey] = Field(None, alias="valueOfParticipation", description="Participation value metadata")
    wachtgeld_old_regulation: Optional[bool] = Field(None, alias="wachtgeldOldRegulation", description="Legacy wachtgeld regulation flag")
    participation55plus_regulation_uwv: Optional[bool] = Field(None, alias="participation55plusRegulationUWV", description="55+ regulation participation flag")
    ess_mutation_set: Optional[MetadataWithKey] = Field(None, alias="essMutationSet", description="ESS mutation set metadata")
    exemption_insurance_obligation: Optional[MetadataWithKey] = Field(None, alias="exemptionInsuranceObligation", description="Insurance obligation exemption metadata")
    special_income_ratio: Optional[MetadataWithKeyAndValue] = Field(None, alias="specialIncomeRatio", description="Special income ratio metadata")
    email_leave_request: Optional[str] = Field(None, alias="emailLeaveRequest", description="Leave request notification email", max_length=255)
    temporary_tax_exemption: Optional[MetadataWithKey] = Field(None, alias="temporaryTaxExemption", description="Temporary tax exemption metadata")
    period_pay_grade_adjustment: Optional[int] = Field(None, alias="periodPayGradeAdjustment", description="Period for pay grade adjustment", ge=1, le=52)
    signal_pay_grade_adjustment: Optional[bool] = Field(None, alias="signalPayGradeAdjustment", description="Pay grade adjustment signal flag")
    is_director_and_major_shareholder: Optional[bool] = Field(None, alias="isDirectorAndMajorShareholder", description="Director and major shareholder flag")
    is_previous_owner: Optional[bool] = Field(None, alias="isPreviousOwner", description="Previous owner flag")
    is_family_of_owner: Optional[bool] = Field(None, alias="isFamilyOfOwner", description="Family of owner flag")
    is_on_call_employment: Optional[bool] = Field(None, alias="isOnCallEmployment", description="On-call employment flag")
    has_on_call_appearance_obligation: Optional[bool] = Field(None, alias="hasOnCallAppearanceObligation", description="On-call appearance obligation flag")
    is_gemoedsbezwaard_national_insurance: Optional[bool] = Field(None, alias="isGemoedsbezwaardNationalInsurance", description="Gemoedsbezwaard national insurance flag")
    is_gemoedsbezwaard_employee_insurance: Optional[bool] = Field(None, alias="isGemoedsbezwaardEmployeeInsurance", description="Gemoedsbezwaard employee insurance flag")
    is_anonymous_employee: Optional[bool] = Field(None, alias="isAnonymousEmployee", description="Anonymous employee flag")
    cancellation_period_employee: Optional[int] = Field(None, alias="cancellationPeriodEmployee", description="Employee cancellation period", ge=1, le=1000)
    cancellation_period_employer: Optional[int] = Field(None, alias="cancellationPeriodEmployer", description="Employer cancellation period", ge=1, le=1000)
    cancellation_period_time_unit: Optional[MetadataWithKey] = Field(None, alias="cancellationPeriodTimeUnit", description="Cancellation period time unit metadata")
    cancellation_notice_date: Optional[str] = Field(None, alias="cancellationNoticeDate", description="Cancellation notice date", examples=["2024-12-01"])
    start_cancellation_notice_period: Optional[str] = Field(None, alias="startCancellationNoticePeriod", description="Start date of cancellation notice period", examples=["2024-12-01"])
    name_payslip: Optional[str] = Field(None, alias="namePayslip", description="Payslip display name", max_length=34)
    calculate_working_hours: Optional[bool] = Field(None, alias="calculateWorkingHours", description="Calculate working hours flag")
    written_employment_contract: Optional[bool] = Field(None, alias="writtenEmploymentContract", description="Written employment contract flag")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"


class EmploymentTerminate(BaseModel):
    """Schema for terminating employment."""
    end_date: str = Field(..., alias="endDate", description="The date on which the employment ends (=last day of the employment)", example="2024-12-31")
    end_of_employment_reason: Optional[MetadataWithKey] = Field(None, alias="endOfEmploymentReason", description="The reason for the end of the employment (legacy field)")
    end_of_employment_due_to_illness: Optional[bool] = Field(None, alias="endOfEmploymentDueToIllness", description="Indicates whether the reason for the termination of an employment is due to long-term illness", example=False)
    create_mdv_entry: Optional[bool] = Field(None, alias="createMdvEntry", description="Indicates whether an MDV-entry should automatically be generated by Loket", example=True)
    end_of_employment_reason_tax_authorities: Optional[MetadataWithKey] = Field(None, alias="endOfEmploymentReasonTaxAuthorities", description="The reason for the end of the employment as specified by the Dutch Tax authorities")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "ignore"
