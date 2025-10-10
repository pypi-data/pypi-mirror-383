from typing import Optional
from datetime import date, datetime
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class SickLeavePeriodGet(BrynQPanderaDataFrameModel):
    """
    Schema for hr2d__SickLeavePer__c entity GET operations.
    Represents sick leave period records in HR2Day system.
    """

    # Standard Salesforce fields
    id: Series[str] = pa.Field(alias="Id", description="Record ID", coerce=True)
    name: Series[str] = pa.Field(alias="Name", description="Period record", coerce=True)
    created_by_id: Series[str] = pa.Field(alias="CreatedById", description="Created By ID", coerce=True)
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", description="Created Date", coerce=True)
    last_activity_date: Optional[Series[datetime]] = pa.Field(alias="LastActivityDate", nullable=True, coerce=True, description="Last Activity Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", description="Last Modified By ID", coerce=True)
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", description="Last Modified Date", coerce=True)
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", description="System Modstamp", coerce=True)

    # Custom fields
    end_date: Optional[Series[date]] = pa.Field(alias="hr2d__EndDate__c", description="End date", coerce=True, nullable=True)
    end_date_filter: Optional[Series[date]] = pa.Field(alias="hr2d__EndDateFilter__c", description="End date (filterfield)", coerce=True)
    sick_leave: Optional[Series[str]] = pa.Field(alias="hr2d__SickLeave__c", description="Sickleave", coerce=True)
    sick_perc: Optional[Series[float]] = pa.Field(alias="hr2d__SickPerc__c", description="Percentage partial sick", coerce=True)
    sick_perc_today: Optional[Series[float]] = pa.Field(alias="hr2d__SickPercToday__c", description="Percentage sickleave today", coerce=True)
    start_date: Optional[Series[date]] = pa.Field(alias="hr2d__StartDate__c", description="Start date", coerce=True)

    class Config:
        """Pandera configuration"""
        strict = "filter"
        add_missing_columns = True
        coerce = True

    class _Annotation:
        """Annotation class for primary and foreign keys"""
        primary_key = "id"
        foreign_keys = {
            "sick_leave": {
                "parent_schema": "SickLeaveGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }
