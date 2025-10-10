from datetime import datetime, date
from pandera.typing import Series
import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class LocationGet(BrynQPanderaDataFrameModel):
    """Schema for hr2d__Location__c entity in HR2Day. Represents a location record."""

    # Salesforce Standard Fields
    id: Series[str] = pa.Field(alias="Id", nullable=False, coerce=True, description="Record ID")
    name: Series[str] = pa.Field(alias="Name", nullable=True, coerce=True, description="Location name")
    created_by_id: Series[str] = pa.Field(alias="CreatedById", nullable=True, coerce=True, description="Created By ID")
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", nullable=True, coerce=True, description="Created Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", nullable=True, coerce=True, description="Last Modified By ID")
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", nullable=True, coerce=True, description="Last Modified Date")
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", nullable=True, coerce=True, description="System Modstamp")

    # HR2Day Custom Fields
    city: Series[str] = pa.Field(alias="hr2d__City__c", nullable=True, coerce=True, description="City of the location")
    country: Series[str] = pa.Field(alias="hr2d__Country__c", nullable=True, coerce=True, description="Country")
    description: Series[str] = pa.Field(alias="hr2d__Description__c", nullable=True, coerce=True, description="Detailed description of the location")
    employer: Series[str] = pa.Field(alias="hr2d__Employer__c", nullable=True, coerce=True, description="Employer")
    end_date: Series[date] = pa.Field(alias="hr2d__EndDate__c", nullable=True, coerce=True, description="Last day the location is valid")
    house_nr: Series[float] = pa.Field(alias="hr2d__HouseNr__c", nullable=True, coerce=True, description="House number without addition")
    house_nr_add: Series[str] = pa.Field(alias="hr2d__HouseNrAdd__c", nullable=True, coerce=True, description="House number addition")
    key: Series[str] = pa.Field(alias="hr2d__Key__c", nullable=True, coerce=True, description="Location key field from employer's wage tax number and location name")
    phone: Series[str] = pa.Field(alias="hr2d__Phone__c", nullable=True, coerce=True, description="Phone number of the location")
    postal_code: Series[str] = pa.Field(alias="hr2d__PostalCode__c", nullable=True, coerce=True, description="Postal code of the location")
    start_date: Series[date] = pa.Field(alias="hr2d__StartDate__c", nullable=True, coerce=True, description="First day the location is valid")
    street: Series[str] = pa.Field(alias="hr2d__Street__c", nullable=True, coerce=True, description="Street name (without house number)")

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
