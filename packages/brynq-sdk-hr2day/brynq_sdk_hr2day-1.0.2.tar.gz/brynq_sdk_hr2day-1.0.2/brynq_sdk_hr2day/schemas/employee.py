from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from pandera.typing import Series
import pandera as pa

from brynq_sdk_functions import BrynQPanderaDataFrameModel

class EmployeeGet(BrynQPanderaDataFrameModel):
    """Schema for hr2d__Employee__c entity GET operations in HR2Day. Represents an employee record."""

    # Base Salesforce fields
    id: Series[str] = pa.Field(alias="Id", nullable=True, description="Record ID", coerce=True)
    is_deleted: Series[bool] = pa.Field(alias="IsDeleted", nullable=True, description="Is deleted flag", coerce=True)
    name: Series[str] = pa.Field(alias="Name", nullable=True, description="Name of the record", coerce=True)
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", nullable=True, description="Created date", coerce=True)
    created_by_id: Series[str] = pa.Field(alias="CreatedById", nullable=True, description="Created by ID", coerce=True)
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", nullable=True, description="Last modified date", coerce=True)
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", nullable=True, description="Last modified by ID", coerce=True)
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", nullable=True, description="System modstamp", coerce=True)
    owner_id: Series[str] = pa.Field(alias="OwnerId", nullable=True, description="Owner ID", coerce=True)

    # HR2Day Custom Fields - Personal Information
    first_name: Series[str] = pa.Field(alias="hr2d__FirstName__c", nullable=True, description="Formal first name of the employee", coerce=True)
    initials: Series[str] = pa.Field(alias="hr2d__Initials__c", nullable=True, description="Initials of the employee, in capitals separated by a dot", coerce=True)
    nickname: Series[str] = pa.Field(alias="hr2d__Nickname__c", nullable=True, description="Nickname of employee (if filled, overrides first name in formatted name)", coerce=True)
    prefix: Series[str] = pa.Field(alias="hr2d__Prefix__c", nullable=True, description="Prefix for employee's surname (birth name)", coerce=True)
    surname: Series[str] = pa.Field(alias="hr2d__Surname__c", nullable=True, description="Employee's surname (birth name)", coerce=True)
    prefix_partner: Series[str] = pa.Field(alias="hr2d__PrefixPartner__c", nullable=True, description="Prefix for partner's surname", coerce=True)
    surname_partner: Series[str] = pa.Field(alias="hr2d__SurnamePartner__c", nullable=True, description="Partner's surname", coerce=True)
    formatted_name: Series[str] = pa.Field(alias="hr2d__A_name__c", nullable=True, description="Formatted name of employee (first name surname - partner name) depending on selected name format", coerce=True)
    formatted_surname: Series[str] = pa.Field(alias="hr2d__A_Surname__c", nullable=True, description="Formatted surname of employee (prefixes surname - partner prefixes partner surname) depending on chosen name format", coerce=True)
    name_format: Series[str] = pa.Field(alias="hr2d__NameFormat__c", nullable=True, description="Controls formatting of employee name (combination of birth name and partner name)", coerce=True)
    title_before: Series[str] = pa.Field(alias="hr2d__TitleBefore__c", nullable=True, description="Title before name", coerce=True)
    title_before_sel: Series[str] = pa.Field(alias="hr2d__TitleBeforeSel__c", nullable=True, description="Title before name (select)", coerce=True)
    title_after: Series[str] = pa.Field(alias="hr2d__TitleAfter__c", nullable=True, description="Title after name", coerce=True)
    title_after_sel: Series[str] = pa.Field(alias="hr2d__TitleAfterSel__c", nullable=True, description="Title after name (select)", coerce=True)
    gender: Series[str] = pa.Field(alias="hr2d__Gender__c", nullable=True, description="Gender of the employee", coerce=True)
    birth_date: Series[datetime] = pa.Field(alias="hr2d__BirthDate__c", nullable=True, description="Date of birth (enter with century indication, dd-mm-yyyy)", coerce=True)
    birthday: Series[datetime] = pa.Field(alias="hr2d__Birthday__c", nullable=True, description="The (next) birthday of the employee", coerce=True)
    birth_place: Series[str] = pa.Field(alias="hr2d__BirthPlace__c", nullable=True, description="Place of birth", coerce=True)
    birth_country: Series[str] = pa.Field(alias="hr2d__BirthCountry__c", nullable=True, description="Country of birth", coerce=True)
    nationality: Series[str] = pa.Field(alias="hr2d__Nationality__c", nullable=True, description="Nationality", coerce=True)
    marital_status: Series[str] = pa.Field(alias="hr2d__MaritalStatus__c", nullable=True, description="Marital status", coerce=True)
    marital_status_date: Series[datetime] = pa.Field(alias="hr2d__MaritalStatusDate__c", nullable=True, description="Date when marital status takes effect", coerce=True)
    death_date: Series[datetime] = pa.Field(alias="hr2d__DeathDate__c", nullable=True, description="Date of death", coerce=True)
    age: Series[float] = pa.Field(alias="hr2d__Age__c", nullable=True, description="Age of employee (today)", coerce=True)
    age_group: Series[str] = pa.Field(alias="hr2d__AgeGroup__c", nullable=True, description="Age group", coerce=True)
    language: Series[str] = pa.Field(alias="hr2d__Language__c", nullable=True, description="Language of the employee", coerce=True)

    # HR2Day Custom Fields - Contact Information
    phone: Series[str] = pa.Field(alias="hr2d__Phone__c", nullable=True, description="Phone number of the employee", coerce=True)
    phone2: Series[str] = pa.Field(alias="hr2d__Phone2__c", nullable=True, description="Second phone number", coerce=True)
    phone3: Series[str] = pa.Field(alias="hr2d__Phone3__c", nullable=True, description="Third phone number", coerce=True)
    email: Series[str] = pa.Field(alias="hr2d__Email__c", nullable=True, description="Private email of the employee", coerce=True)
    email_work: Series[str] = pa.Field(alias="hr2d__EmailWork__c", nullable=True, description="Work email of the employee", coerce=True)
    workplace: Series[str] = pa.Field(alias="hr2d__Workplace__c", nullable=True, description="Workplace/room number", coerce=True)

    # HR2Day Custom Fields - Employment Information
    empl_nr: Series[float] = pa.Field(alias="hr2d__EmplNr__c", nullable=True, description="Employee number", coerce=True)
    empl_nr_alt: Series[str] = pa.Field(alias="hr2d__EmplNr_Alt__c", nullable=True, description="Alternative employee number", coerce=True)
    alias: Series[str] = pa.Field(alias="hr2d__Alias__c", nullable=True, description="Employee alias", coerce=True)
    hire_date: Series[datetime] = pa.Field(alias="hr2d__HireDate__c", nullable=True, description="Date of employment", coerce=True)
    hire_date_concern: Series[datetime] = pa.Field(alias="hr2d__HireDateConcern__c", nullable=True, description="Date employee joined the concern (seniority)", coerce=True)
    termination_date: Series[datetime] = pa.Field(alias="hr2d__TerminationDate__c", nullable=True, description="End date of employment (last day employee was still employed)", coerce=True)
    retirement_date: Series[datetime] = pa.Field(alias="hr2d__RetirementDate__c", nullable=True, description="Expected AOW/pension date based on current legislation", coerce=True)
    seniority: Series[float] = pa.Field(alias="hr2d__Seniority__c", nullable=True, description="Number of years of service of the employee (today)", coerce=True)
    education_level: Series[str] = pa.Field(alias="hr2d__EducationLevel__c", nullable=True, description="Highest education completed", coerce=True)
    employer: Series[str] = pa.Field(alias="hr2d__Employer__c", nullable=True, description="Employer", coerce=True)
    employment_relationship_today: Series[str] = pa.Field(alias="hr2d__ArbeidsrelatieToday__c", nullable=True, description="Current valid employment relationship", coerce=True)
    department_today: Series[str] = pa.Field(alias="hr2d__DepartmentToday__c", nullable=True, description="Current department", coerce=True)
    job_today: Series[str] = pa.Field(alias="hr2d__JobToday__c", nullable=True, description="Current job", coerce=True)
    wtf_total_today: Series[float] = pa.Field(alias="hr2d__WtfTotalToday__c", nullable=True, description="Current total part-time factor", coerce=True)
    mentor: Series[str] = pa.Field(alias="hr2d__Mentor__c", nullable=True, description="Employee who is mentor of this employee", coerce=True)

    # HR2Day Custom Fields - Address Information
    street: Series[str] = pa.Field(alias="hr2d__Street__c", nullable=True, description="Street name (without house number)", coerce=True)
    house_nr: Series[float] = pa.Field(alias="hr2d__HouseNr__c", nullable=True, description="House number without addition", coerce=True)
    house_nr_add: Series[str] = pa.Field(alias="hr2d__HouseNrAdd__c", nullable=True, description="House number addition", coerce=True)
    add_address_line: Series[str] = pa.Field(alias="hr2d__AddAddressLine__c", nullable=True, description="Additional address line", coerce=True)
    postal_code: Series[str] = pa.Field(alias="hr2d__PostalCode__c", nullable=True, description="Postal code", coerce=True)
    city: Series[str] = pa.Field(alias="hr2d__City__c", nullable=True, description="City", coerce=True)
    country: Series[str] = pa.Field(alias="hr2d__Country__c", nullable=True, description="Country (ISO code)", coerce=True)

    # HR2Day Custom Fields - Bank Information
    bank: Series[str] = pa.Field(alias="hr2d__Bank__c", nullable=True, description="Bank account number", coerce=True)
    bank_iban: Series[str] = pa.Field(alias="hr2d__BankIBAN__c", nullable=True, description="International Bank Account Number", coerce=True)
    bank_bic: Series[str] = pa.Field(alias="hr2d__BankBIC__c", nullable=True, description="Bank Identification Code (BIC or formerly SWIFT code)", coerce=True)
    bank_name: Series[str] = pa.Field(alias="hr2d__BankName__c", nullable=True, description="Alternative bank account holder name", coerce=True)
    bank_description: Series[str] = pa.Field(alias="hr2d__Bank_Description__c", nullable=True, description="Alternative description for bank payment", coerce=True)

    # HR2Day Custom Fields - User Information
    user: Series[str] = pa.Field(alias="hr2d__User__c", nullable=True, description="Salesforce user for Employee Self Service", coerce=True)
    user_additional: Series[str] = pa.Field(alias="hr2d__UserAdditional__c", nullable=True, description="Additional user account with different authorizations", coerce=True)
    default_username: Series[str] = pa.Field(alias="hr2d__DefaultUserName__c", nullable=True, description="Standard username when creating user", coerce=True)
    bundel_id: Series[str] = pa.Field(alias="hr2d__BundelId__c", nullable=True, description="SAML Bundle Id for user creation", coerce=True)
    inbox_settings: Series[str] = pa.Field(alias="hr2d__InboxSettings__c", nullable=True, description="Inbox settings for this employee", coerce=True)
    portfolio_settings: Series[str] = pa.Field(alias="hr2d__PortfolioSettings__c", nullable=True, description="Portfolio settings", coerce=True)
    portfolio_permission: Series[str] = pa.Field(alias="hr2d__PortfolioPermission__c", nullable=True, description="Portfolio permissions", coerce=True)
    privacy_settings: Series[str] = pa.Field(alias="hr2d__PrivacySettings__c", nullable=True, description="Privacy settings of this employee", coerce=True)
    payslip_settings: Series[str] = pa.Field(alias="hr2d__PayslipSettings__c", nullable=True, description="Pay slip settings", coerce=True)

    # HR2Day Custom Fields - System Fields
    last_activity_date: Optional[Series[datetime]] = pa.Field(alias="LastActivityDate", nullable=True, description="Last activity date", coerce=True)
    last_viewed_date: Series[datetime] = pa.Field(alias="LastViewedDate", nullable=True, description="Last viewed date", coerce=True)
    last_referenced_date: Series[datetime] = pa.Field(alias="LastReferencedDate", nullable=True, description="Last referenced date", coerce=True)
    record_id: Series[str] = pa.Field(alias="hr2d__RecordId__c", nullable=True, description="Case insensitive record ID", coerce=True)
    termination_date_filter: Series[str] = pa.Field(alias="hr2d__TerminationDateFilter__c", nullable=True, description="Termination date filter", coerce=True)
    external_key: Series[str] = pa.Field(alias="hr2d__ExternalKey__c", nullable=True, description="External key", coerce=True)
    key: Series[str] = pa.Field(alias="hr2d__Key__c", nullable=True, description="Key", coerce=True)
    search_name: Series[str] = pa.Field(alias="hr2d__SearchName__c", nullable=True, description="The name used for searching without diacritics", coerce=True)

    # HR2Day Custom Fields - Additional Fields
    absent_today: Series[bool] = pa.Field(alias="hr2d__AbsentToday__c", nullable=True, description="Indication if employee is absent today", coerce=True)
    bsn: Series[str] = pa.Field(alias="hr2d__BSN__c", nullable=True, description="Citizen service number (BSN/SoFi number)", coerce=True)
    id_end_date: Series[datetime] = pa.Field(alias="hr2d__ID_EndDate__c", nullable=True, description="ID expiration date", coerce=True)
    id_number: Series[str] = pa.Field(alias="hr2d__ID_Nr__c", nullable=True, description="ID number", coerce=True)
    id_issue_date: Series[datetime] = pa.Field(alias="hr2d__ID_RelDate__c", nullable=True, description="ID date of issue", coerce=True)
    id_type: Series[str] = pa.Field(alias="hr2d__ID_Type__c", nullable=True, description="Type of identification document", coerce=True)
    leave_today_until: Series[datetime] = pa.Field(alias="hr2d__LeaveTodayUntil__c", nullable=True, description="If on leave today, until when", coerce=True)
    empl_nr_plain: Series[str] = pa.Field(alias="hr2d__EmplNr_plain__c", nullable=True, description="Employee number plain", coerce=True)
    proforma_employee: Series[str] = pa.Field(alias="hr2d__ProformaEmployee__c", nullable=True, description="Employee from which this employee record is derived for proforma payroll", coerce=True)
    rooster_code: Series[str] = pa.Field(alias="hr2d__Roostercode__c", nullable=True, description="Rooster code", coerce=True)
    sick_perc_today: Series[float] = pa.Field(alias="hr2d__SickPercToday__c", nullable=True, description="Sick leave percentage today", coerce=True)
    sideline_jobs: Series[bool] = pa.Field(alias="hr2d__SidelineJobs__c", nullable=True, description="Check if employee has sideline jobs", coerce=True)
    sideline_jobs_description: Series[str] = pa.Field(alias="hr2d__SidelineJobsDescription__c", nullable=True, description="Description of sideline jobs", coerce=True)
    signature: Series[str] = pa.Field(alias="hr2d__Signature__c", nullable=True, description="Employee signature", coerce=True)
    signature_id: Series[str] = pa.Field(alias="hr2d__SignatureId__c", nullable=True, description="ID of attachment used as signature", coerce=True)

    # HR2Day Custom Fields - Postal Address
    mail_add_address_line: Series[str] = pa.Field(alias="hr2d__Mail_AddAddressLine__c", nullable=True, description="Additional address line for postal address", coerce=True)
    mail_city: Series[str] = pa.Field(alias="hr2d__Mail_City__c", nullable=True, description="City of postal address", coerce=True)
    mail_country: Series[str] = pa.Field(alias="hr2d__Mail_Country__c", nullable=True, description="Country of postal address (ISO code)", coerce=True)
    mail_house_nr: Series[float] = pa.Field(alias="hr2d__Mail_HouseNr__c", nullable=True, description="House number of postal address (without addition)", coerce=True)
    mail_house_nr_add: Series[str] = pa.Field(alias="hr2d__Mail_HouseNrAdd__c", nullable=True, description="Addition to house number of postal address", coerce=True)
    mail_postal_code: Series[str] = pa.Field(alias="hr2d__Mail_PostalCode__c", nullable=True, description="Postal code of postal address", coerce=True)
    mail_street: Series[str] = pa.Field(alias="hr2d__Mail_Street__c", nullable=True, description="Street of postal address (without house number)", coerce=True)
    mail_address_copy: Series[bool] = pa.Field(alias="hr2d__MailAddress_Copy__c", nullable=True, description="Copy postal address from standard address", coerce=True)

    # HR2Day Custom Fields - Photo
    picture: Series[str] = pa.Field(alias="hr2d__Picture__c", nullable=True, description="Photo", coerce=True)
    picture_id: Series[str] = pa.Field(alias="hr2d__PictureID__c", nullable=True, description="Photo ID", coerce=True)
    picture_small_id: Series[str] = pa.Field(alias="hr2d__PictureSmallId__c", nullable=True, description="Photo Small ID", coerce=True)

    # Custom Fields
    bonus: Series[bool] = pa.Field(alias="Bonus__c", nullable=True, description="Bonus flag", coerce=True)
    inleners: Series[str] = pa.Field(alias="Inleners__c", nullable=True, description="Inleners field", coerce=True)
    jub_cor: Series[str] = pa.Field(alias="JubCor__c", nullable=True, description="Jubilee correction", coerce=True)
    jub_125: Series[datetime] = pa.Field(alias="Jub125__c", nullable=True, description="12.5 year jubilee date", coerce=True)
    jub_10: Series[datetime] = pa.Field(alias="Jub10__c", nullable=True, description="10 year jubilee date", coerce=True)
    jub_15: Series[datetime] = pa.Field(alias="Jub15__c", nullable=True, description="15 year jubilee date", coerce=True)
    jub_25: Series[datetime] = pa.Field(alias="Jub25__c", nullable=True, description="25 year jubilee date", coerce=True)
    jub_40: Series[datetime] = pa.Field(alias="Jub40__c", nullable=True, description="40 year jubilee date", coerce=True)

    class _Annotation:
        """Primary and foreign key annotations for Employee entity"""
        primary_key = "id"
        foreign_keys = {
            "employer": {
                "parent_schema": "EmployerGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "department_today": {
                "parent_schema": "DepartmentGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "job_today": {
                "parent_schema": "JobGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "employment_relationship_today": {
                "parent_schema": "EmploymentRelationshipGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

    class Config:
        """Schema configuration"""
        strict="filter"  # Allow extra columns not defined in schema
        coerce = True
        add_missing_columns = True  # Add missing columns as nullable


class EmployeeUpdateFields(BaseModel):
    """Schema for updatable employee fields in HR2Day API."""
    email: Optional[str] = Field(None, alias="hr2d__Email__c", description="Private email (in email format a@b.c)")
    email_work: Optional[str] = Field(None, alias="hr2d__EmailWork__c", description="Work email (in email format a@b.c)")
    phone: Optional[str] = Field(None, alias="hr2d__Phone__c", description="Phone number (max 20 characters)")
    phone2: Optional[str] = Field(None, alias="hr2d__Phone2__c", description="Second phone number (max 20 characters)")
    phone3: Optional[str] = Field(None, alias="hr2d__Phone3__c", description="Third phone number (max 20 characters)")
    workplace: Optional[str] = Field(None, alias="hr2d__Workplace__c", description="Workplace (max 25 characters)")
    default_username: Optional[str] = Field(None, alias="hr2d__DefaultUsername__c", description="Default username (max 80 characters)")
    bundel_id: Optional[str] = Field(None, alias="hr2d__BundelId__c", description="SAML Bundle Id (max 60 characters)")
    empl_nr_alt: Optional[str] = Field(None, alias="hr2d__EmplNr_Alt__c", description="Alternative personnel number (max 20 characters)")

    class Config:
        """Pydantic configuration"""
        frozen = False
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "forbid"


class EmployeeUpdate(BaseModel):
    """Schema for employee update request in HR2Day API."""
    employer_id: Optional[str] = Field(None, alias="employerId", description="Employer ID (18 characters, case sensitive)")
    employer_name: Optional[str] = Field(None, alias="employerName", description="Employer name (max 80 characters, case sensitive)")
    employer_tax_id: Optional[str] = Field(None, alias="employerTaxId", description="Employer tax ID (12 characters, case sensitive)")
    employee_id: Optional[str] = Field(None, alias="employeeId", description="Employee ID (18 characters, case sensitive)")
    employee_key: Optional[str] = Field(None, alias="employeeKey", description="Employee Key (22 characters, case sensitive)")
    employee_emplnr: Optional[str] = Field(None, alias="employeeEmplnr", description="Employee number (max 10 characters, numeric)")
    employee_emplnr_alternative: Optional[str] = Field(None, alias="employeeEmplnrAlternative", description="Alternative employee number (max 10 characters, case sensitive)")
    errors: Optional[str] = Field("", description="Error messages for this employee update")
    employee: EmployeeUpdateFields = Field(..., description="Employee fields to update")

    @field_validator('employee_emplnr')
    @classmethod
    def validate_employee_emplnr(cls, v, info):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Employee number must be at most 10 characters')
            try:
                int(v)  # Check if it can be converted to integer
            except ValueError:
                raise ValueError('Employee number must be numeric')

            # Check if employer identifier is provided
            data = info.data
            if not data.get('employer_id') and not data.get('employer_name') and not data.get('employer_tax_id'):
                raise ValueError('When using employee_emplnr, one of employer_id, employer_name, or employer_tax_id is required')
        return v

    @field_validator('employee_emplnr_alternative')
    @classmethod
    def validate_employee_emplnr_alt(cls, v, info):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Alternative employee number must be at most 10 characters')
            # Check if employer identifier is provided
            data = info.data
            if not data.get('employer_id') and not data.get('employer_name') and not data.get('employer_tax_id'):
                raise ValueError('When using employee_emplnr_alternative, one of employer_id, employer_name, or employer_tax_id is required')
        return v

    @field_validator('employee')
    @classmethod
    def validate_employee_fields(cls, v):
        # Ensure at least one field is provided for update
        if not any(getattr(v, field) is not None for field in v.__fields__):
            raise ValueError('At least one employee field must be provided for update')
        return v

    # Validate that at least one employee identifier is provided
    @field_validator('employee_id', 'employee_key', 'employee_emplnr', 'employee_emplnr_alternative')
    @classmethod
    def validate_employee_identifier(cls, v, info):
        field_name = info.field_name
        if field_name == 'employee_emplnr_alternative':
            data = info.data
            if not any([
                data.get('employee_id'),
                data.get('employee_key'),
                data.get('employee_emplnr'),
                v
            ]):
                raise ValueError('At least one of employee_id, employee_key, employee_emplnr, or employee_emplnr_alternative must be provided')
        return v

    class Config:
        """Pydantic configuration"""
        frozen = False
        strict = True
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = "forbid"
