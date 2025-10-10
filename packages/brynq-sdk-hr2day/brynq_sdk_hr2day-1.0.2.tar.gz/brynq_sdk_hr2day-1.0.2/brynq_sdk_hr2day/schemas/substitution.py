from typing import Optional
from datetime import date, datetime
from pandera.typing import Series
import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class SubstitutionGet(BrynQPanderaDataFrameModel):
    """
    Schema for hr2d__Substitution__c entity GET operations.
    Represents substitution records in HR2Day system.
    """

    # Standard Salesforce fields
    id: Series[str] = pa.Field(alias="Id", description="Record ID", coerce=True)
    name: Series[str] = pa.Field(alias="Name", description="Substitution", coerce=True)
    created_by_id: Series[str] = pa.Field(alias="CreatedById", description="Created By ID", coerce=True)
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", description="Created Date", coerce=True)
    last_activity_date: Optional[Series[datetime]] = pa.Field(alias="LastActivityDate", nullable=True, coerce=True, description="Last Activity Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", description="Last Modified By ID", coerce=True)
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", description="Last Modified Date", coerce=True)
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", description="System Modstamp", coerce=True)

    # Custom fields
    employment_sequence_number: Optional[Series[float]] = pa.Field(alias="hr2d__ArbrelVolgnr__c", nullable=True, description="Employment sequence number", coerce=True)
    block_transfer: Optional[Series[bool]] = pa.Field(alias="hr2d__BlockTransfer__c", nullable=True, description="Lock transfer", coerce=True)
    calendar_days: Optional[Series[float]] = pa.Field(alias="hr2d__CalDays__c", nullable=True, description="Calendar days", coerce=True)
    cost_center: Optional[Series[str]] = pa.Field(alias="hr2d__CostCenter__c", nullable=True, description="Cost center", coerce=True)
    cost_center_dim2: Optional[Series[str]] = pa.Field(alias="hr2d__CostCenter_Dim2__c", nullable=True, description="Cost center Dim2", coerce=True)
    cost_center_dim3: Optional[Series[str]] = pa.Field(alias="hr2d__CostCenter_Dim3__c", nullable=True, description="Cost center Dim3", coerce=True)
    date_time_last_collective_document: Optional[Series[datetime]] = pa.Field(alias="hr2d__DateTimeLastVerzamelakte__c", nullable=True, description="Date last collective document", coerce=True)
    declarable: Optional[Series[bool]] = pa.Field(alias="hr2d__Declarabel__c", nullable=True, description="Billable", coerce=True)
    department: Optional[Series[str]] = pa.Field(alias="hr2d__Department__c", nullable=True, description="Department", coerce=True)
    end_date: Optional[Series[date]] = pa.Field(alias="hr2d__EndDate__c", nullable=True, description="End date", coerce=True)
    external_key: Optional[Series[str]] = pa.Field(alias="hr2d__ExternalKey__c", nullable=True, description="External key", coerce=True)
    lock_indication: Optional[Series[str]] = pa.Field(alias="hr2d__FinBron__c", nullable=True, description="Lock indication", coerce=True)
    key: Optional[Series[str]] = pa.Field(alias="hr2d__Key__c", nullable=True, description="Key", coerce=True)
    last_modified_date_time_document: Optional[Series[datetime]] = pa.Field(alias="hr2d__LastModifiedDateTimeAkte__c", nullable=True, description="Last modified date for documents", coerce=True)
    leave: Optional[Series[str]] = pa.Field(alias="hr2d__Leave__c", nullable=True, description="Leave record", coerce=True)
    original_created_date: Optional[Series[datetime]] = pa.Field(alias="hr2d__OriginalCreateddate__c", nullable=True, description="Created date", coerce=True)
    original_name: Optional[Series[str]] = pa.Field(alias="hr2d__OriginalName__c", nullable=True, description="Original name", coerce=True)
    processed: Optional[Series[str]] = pa.Field(alias="hr2d__Processed__c", nullable=True, description="Processed", coerce=True)
    record_id: Optional[Series[str]] = pa.Field(alias="hr2d__RecordId__c", nullable=True, description="Record ID (long)", coerce=True)
    shift: Optional[Series[str]] = pa.Field(alias="hr2d__Rooster__c", nullable=True, description="Shift", coerce=True)
    sick_leave: Optional[Series[str]] = pa.Field(alias="hr2d__SickLeave__c", nullable=True, description="Sick leave record", coerce=True)
    kind_of_substitute: Optional[Series[str]] = pa.Field(alias="hr2d__SrtVervanger__c", nullable=True, description="Kind of substitute", coerce=True)
    start_date: Optional[Series[date]] = pa.Field(alias="hr2d__StartDate__c", nullable=True, description="Start date", coerce=True)
    substitute: Optional[Series[str]] = pa.Field(alias="hr2d__Vervanger__c", nullable=True, description="Substitute", coerce=True)
    work_time_factor_first_month: Optional[Series[float]] = pa.Field(alias="hr2d__WtfEersteMaand__c", nullable=True, description="Work time factor first month", coerce=True)
    work_time_factor_last_month: Optional[Series[float]] = pa.Field(alias="hr2d__WtfLaatsteMaand__c", nullable=True, description="Work time factor last month", coerce=True)
    work_time_factor_month: Optional[Series[float]] = pa.Field(alias="hr2d__WtfMaand__c", nullable=True, description="Work time factor month", coerce=True)

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
            },
            "leave": {
                "parent_schema": "LeaveGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "substitute": {
                "parent_schema": "EmployeeGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "department": {
                "parent_schema": "DepartmentGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "cost_center": {
                "parent_schema": "CostCenterGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }
