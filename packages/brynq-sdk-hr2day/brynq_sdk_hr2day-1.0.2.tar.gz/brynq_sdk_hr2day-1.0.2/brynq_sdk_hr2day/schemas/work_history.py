from typing import Optional
from datetime import date, datetime
from pandera.typing import Series
import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class WorkHistoryGet(BrynQPanderaDataFrameModel):
    """
    Schema for hr2d__arbeidsverleden__c entity GET operations.
    Represents work history records in HR2Day system.
    """

    # Standard Salesforce fields
    id: Series[str] = pa.Field(alias="Id", description="Record ID", coerce=True)
    name: Series[str] = pa.Field(alias="Name", description="Work history", coerce=True)
    created_by_id: Series[str] = pa.Field(alias="CreatedById", description="Created By ID", coerce=True)
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", description="Created Date", coerce=True)
    last_activity_date: Optional[Series[datetime]] = pa.Field(alias="LastActivityDate", nullable=True, coerce=True, description="Last Activity Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", description="Last Modified By ID", coerce=True)
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", description="Last Modified Date", coerce=True)
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", description="System Modstamp", coerce=True)

    # Custom fields
    lay_off: Optional[Series[bool]] = pa.Field(alias="hr2d__Afvloeiing__c", nullable=True, description="Lay-off", coerce=True)
    approved: Optional[Series[bool]] = pa.Field(alias="hr2d__Approved__c", nullable=True, description="Approval employee", coerce=True)
    approved_date: Optional[Series[date]] = pa.Field(alias="hr2d__ApprovedDate__c", nullable=True, description="Approval date", coerce=True)
    jubilee_category_1: Optional[Series[str]] = pa.Field(alias="hr2d__Cat1__c", nullable=True, description="Jubilee category 1", coerce=True)
    jubilee_category_2: Optional[Series[str]] = pa.Field(alias="hr2d__Cat2__c", nullable=True, description="Jubilee category 2", coerce=True)
    jubilee_category_3: Optional[Series[str]] = pa.Field(alias="hr2d__Cat3__c", nullable=True, description="Jubilee category 3", coerce=True)
    jubilee_category_4: Optional[Series[str]] = pa.Field(alias="hr2d__Cat4__c", nullable=True, description="Jubilee category 4", coerce=True)
    count_in_category_1: Optional[Series[bool]] = pa.Field(alias="hr2d__CountCat1__c", nullable=True, description="Count in 1", coerce=True)
    count_in_category_2: Optional[Series[bool]] = pa.Field(alias="hr2d__CountCat2__c", nullable=True, description="Count in 2", coerce=True)
    count_in_category_3: Optional[Series[bool]] = pa.Field(alias="hr2d__CountCat3__c", nullable=True, description="Count in 3", coerce=True)
    count_in_category_4: Optional[Series[bool]] = pa.Field(alias="hr2d__CountCat4__c", nullable=True, description="Count in 4", coerce=True)
    employee: Optional[Series[str]] = pa.Field(alias="hr2d__Employee__c", nullable=True, description="Employee", coerce=True)
    end_date: Optional[Series[date]] = pa.Field(alias="hr2d__EndDate__c", nullable=True, description="End date", coerce=True)
    notes: Optional[Series[str]] = pa.Field(alias="hr2d__Notes__c", nullable=True, description="Notes", coerce=True)
    start_date: Optional[Series[date]] = pa.Field(alias="hr2d__StartDate__c", nullable=True, description="Start date", coerce=True)
    employer: Optional[Series[str]] = pa.Field(alias="hr2d__Werkgever__c", nullable=True, description="Employer", coerce=True)
    number_of_years: Optional[Series[float]] = pa.Field(alias="hr2d__Years__c", nullable=True, description="Number of years", coerce=True)

    class Config:
        """Pandera configuration"""
        strict = "filter"
        add_missing_columns = True
        coerce = True

    class _Annotation:
        """Annotation class for primary and foreign keys"""
        primary_key = "id"
        foreign_keys = {
            "employee": {
                "parent_schema": "EmployeeGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }
