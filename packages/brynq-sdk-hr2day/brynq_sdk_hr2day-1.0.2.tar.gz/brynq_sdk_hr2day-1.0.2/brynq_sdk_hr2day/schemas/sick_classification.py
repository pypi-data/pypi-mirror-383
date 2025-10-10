from typing import Optional
from datetime import datetime
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class SickClassificationGet(BrynQPanderaDataFrameModel):
    """
    Schema for hr2d__SickClassification__c entity GET operations.
    Represents sick leave classification records in HR2Day system.
    """

    # Standard Salesforce fields
    id: Series[str] = pa.Field(alias="Id", description="Record ID", coerce=True)
    name: Series[str] = pa.Field(alias="Name", description="Name", coerce=True)
    created_by_id: Series[str] = pa.Field(alias="CreatedById", description="Created By ID", coerce=True)
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", description="Created Date", coerce=True)
    last_activity_date: Optional[Series[datetime]] = pa.Field(alias="LastActivityDate", nullable=True, coerce=True, description="Last Activity Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", description="Last Modified By ID", coerce=True)
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", description="Last Modified Date", coerce=True)
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", description="System Modstamp", coerce=True)

    # Custom fields
    employer: Optional[Series[str]] = pa.Field(alias="hr2d__Employer__c", description="Employer reference", coerce=True)
    type: Optional[Series[str]] = pa.Field(alias="hr2d__Type__c", description="Classification type", coerce=True)

    class Config:
        """Pandera configuration"""
        strict = "filter"
        add_missing_columns = True
        coerce = True

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
