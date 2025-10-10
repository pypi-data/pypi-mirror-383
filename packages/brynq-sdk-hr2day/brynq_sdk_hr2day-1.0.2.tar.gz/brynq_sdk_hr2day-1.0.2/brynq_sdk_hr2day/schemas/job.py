from datetime import datetime, date
from pandera.typing import Series
from typing import Optional
import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class JobGet(BrynQPanderaDataFrameModel):
    """Schema for hr2d__Job__c entity in HR2Day. Represents a job record."""

    # Salesforce Standard Fields
    id: Series[str] = pa.Field(alias="Id", nullable=False, coerce=True, description="Record ID")
    name: Series[str] = pa.Field(alias="Name", nullable=True, coerce=True, description="Name/code")
    created_by_id: Series[str] = pa.Field(alias="CreatedById", nullable=True, coerce=True, description="Created By ID")
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", nullable=True, coerce=True, description="Created Date")
    last_activity_date: Optional[Series[datetime]] = pa.Field(alias="LastActivityDate", nullable=True, coerce=True, description="Last Activity Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", nullable=True, coerce=True, description="Last Modified By ID")
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", nullable=True, coerce=True, description="Last Modified Date")
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", nullable=True, coerce=True, description="System Modstamp")

    # HR2Day Custom Fields
    competence_profile: Series[str] = pa.Field(alias="hr2d__Competenceprofile__c", nullable=True, coerce=True, description="Competence profile with competence levels")
    description: Series[str] = pa.Field(alias="hr2d__Description__c", nullable=True, coerce=True, description="Description")
    description_short: Series[str] = pa.Field(alias="hr2d__DescriptionShort__c", nullable=True, coerce=True, description="Short description of the job")
    description_short_en: Series[str] = pa.Field(alias="hr2d__DescriptionShort_EN__c", nullable=True, coerce=True, description="Short description of the job in English")
    employer: Series[str] = pa.Field(alias="hr2d__Employer__c", nullable=True, coerce=True, description="Employer where this job is defined")
    end_date: Optional[Series[date]] = pa.Field(alias="hr2d__EndDate__c", nullable=True, coerce=True, description="Last day the job is valid")
    job_category: Series[str] = pa.Field(alias="hr2d__JobCategory__c", nullable=True, coerce=True, description="Job category")
    job_char: Series[str] = pa.Field(alias="hr2d__JobChar__c", nullable=True, coerce=True, description="Job identification")
    job_classification: Series[str] = pa.Field(alias="hr2d__JobClassification__c", nullable=True, coerce=True, description="Job classification")
    job_family: Series[str] = pa.Field(alias="hr2d__JobFamily__c", nullable=True, coerce=True, description="Job family")
    job_nr: Series[str] = pa.Field(alias="hr2d__JobNr__c", nullable=True, coerce=True, description="Job number")
    job_schaal: Series[str] = pa.Field(alias="hr2d__JobSchaal__c", nullable=True, coerce=True, description="Payscale")
    key: Series[str] = pa.Field(alias="hr2d__Key__c", nullable=True, coerce=True, description="Key")
    name_en: Series[str] = pa.Field(alias="hr2d__Name_EN__c", nullable=True, coerce=True, description="Name in English")
    name_alternative: Series[str] = pa.Field(alias="hr2d__NameAlternative__c", nullable=True, coerce=True, description="Alternative name")
    start_date: Optional[Series[date]] = pa.Field(alias="hr2d__StartDate__c", nullable=True, coerce=True, description="First day the job is valid")

    class _Annotation:
        """Annotation class for primary and foreign keys"""
        primary_key = "id"
        foreign_keys = {
            "employer": {
                "parent_schema": "EmployerGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

    class Config:
        """Schema configuration"""
        strict = "filter"  # Allow extra columns not defined in schema
        coerce = True
        add_missing_columns = True  # Add missing columns as nullable
