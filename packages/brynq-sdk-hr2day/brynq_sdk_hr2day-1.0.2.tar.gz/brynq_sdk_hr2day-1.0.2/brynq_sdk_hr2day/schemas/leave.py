from typing import Optional, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field
from pandera.typing import Series
import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class LeaveCreate(BaseModel):
    """Schema for creating leave records (POST operations)"""
    # API Fields
    external_key: Optional[str] = Field(None, alias="hr2d__ExternalKey__c", description="External key", coerce=True)
    internal_id: Optional[str] = Field(None, alias="hr2d__InternalId__c", description="Internal ID", coerce=True)
    employee_id: Optional[str] = Field(None, alias="hr2d__EmployeeId__c", description="Employee ID", coerce=True)
    employee_number: Optional[str] = Field(None, alias="hr2d__EmployeeNr__c", description="Employee number", coerce=True)
    mode: Literal["online"] = Field(alias="hr2d__Mode__c", description="Mode", coerce=True)
    operation: Literal["insert", "update", "delete"] = Field(alias="hr2d__Operation__c", description="Operation", coerce=True)
    employer_id: Optional[str] = Field(None, alias="hr2d__EmployerId__c", description="Employer ID", coerce=True)
    employer_tax_id: Optional[str] = Field(None, alias="hr2d__EmployerTaxId__c", description="Employer tax ID", coerce=True)
    employer_name: Optional[str] = Field(None, alias="hr2d__EmployerName__c", description="Employer name", coerce=True)

    # Leave Fields
    hours: Optional[float] = Field(None, alias="hr2d__Hours__c", ge=0, description="Number of hours", coerce=True)
    start_date: Optional[date] = Field(None, alias="hr2d__StartDate__c", description="Start date", coerce=True)
    end_date: Optional[date] = Field(None, alias="hr2d__EndDate__c", description="End date", coerce=True)
    employment_sequence_number: Optional[int] = Field(None, alias="hr2d__ArbrelVolgnr__c", ge=0, description="Employment sequence number", coerce=True)
    reason: Optional[str] = Field(None, alias="hr2d__Reason__c", description="Reason", coerce=True)
    details: Optional[str] = Field(None, alias="hr2d__Details__c", description="Details", coerce=True)
    time_in_lieu_type: Optional[Literal["Opboeking (uren gewerkt die later opgenomen kunnen worden)", "Afboeking (uren opnemen)"]] = Field(None, alias="hr2d__TvtType__c", description="Time in lieu type", coerce=True)
    description: Optional[str] = Field(None, alias="hr2d__Description__c", description="Description", coerce=True)
    leave_code: Optional[str] = Field(None, alias="hr2d__LeaveCode__c", description="Leave code", coerce=True)
    leave_type: Optional[str] = Field(None, alias="hr2d__Leave__c", description="Leave type", coerce=True)
    changes: Optional[str] = Field(None, alias="hr2d__Changes__c", description="Changes", coerce=True)
    workflow_status: Optional[Literal["Goedgekeurd", "Ingetrokken"]] = Field(None, alias="hr2d__Workflowstatus__c", description="Workflow status", coerce=True)

    class Config:
        """Schema configuration"""
        coerce = True
        strict = False
        populate_by_name = True


class LeaveUpdate(BaseModel):
    """Schema for updating leave records (PUT operations)"""
    # API Fields
    external_key: Optional[str] = Field(None, alias="hr2d__ExternalKey__c", description="External key", coerce=True)
    internal_id: Optional[str] = Field(None, alias="hr2d__InternalId__c", description="Internal ID", coerce=True)
    employee_id: Optional[str] = Field(None, alias="hr2d__EmployeeId__c", description="Employee ID", coerce=True)
    employee_number: Optional[str] = Field(None, alias="hr2d__EmployeeNr__c", description="Employee number", coerce=True)
    mode: Literal["online"] = Field(alias="hr2d__Mode__c", description="Mode", coerce=True)
    operation: Literal["insert", "update", "delete"] = Field(alias="hr2d__Operation__c", description="Operation", coerce=True)
    employer_id: Optional[str] = Field(None, alias="hr2d__EmployerId__c", description="Employer ID", coerce=True)
    employer_tax_id: Optional[str] = Field(None, alias="hr2d__EmployerTaxId__c", description="Employer tax ID", coerce=True)
    employer_name: Optional[str] = Field(None, alias="hr2d__EmployerName__c", description="Employer name", coerce=True)

    # Leave Fields
    hours: Optional[float] = Field(None, alias="hr2d__Hours__c", ge=0, description="Number of hours", coerce=True)
    start_date: Optional[date] = Field(None, alias="hr2d__StartDate__c", description="Start date", coerce=True)
    end_date: Optional[date] = Field(None, alias="hr2d__EndDate__c", description="End date", coerce=True)
    employment_sequence_number: Optional[int] = Field(None, alias="hr2d__ArbrelVolgnr__c", ge=0, description="Employment sequence number", coerce=True)
    reason: Optional[str] = Field(None, alias="hr2d__Reason__c", description="Reason", coerce=True)
    details: Optional[str] = Field(None, alias="hr2d__Details__c", description="Details", coerce=True)
    time_in_lieu_type: Optional[Literal["Opboeking (uren gewerkt die later opgenomen kunnen worden)", "Afboeking (uren opnemen)"]] = Field(None, alias="hr2d__TvtType__c", description="Time in lieu type", coerce=True)
    description: Optional[str] = Field(None, alias="hr2d__Description__c", description="Description", coerce=True)
    leave_code: Optional[str] = Field(None, alias="hr2d__LeaveCode__c", description="Leave code", coerce=True)
    leave_type: Optional[str] = Field(None, alias="hr2d__Leave__c", description="Leave type", coerce=True)
    changes: Optional[str] = Field(None, alias="hr2d__Changes__c", description="Changes", coerce=True)
    workflow_status: Optional[Literal["Goedgekeurd", "Ingetrokken"]] = Field(None, alias="hr2d__Workflowstatus__c", description="Workflow status", coerce=True)

    class Config:
        """Schema configuration"""
        coerce = True
        strict = False
        populate_by_name = True


class LeaveGet(BrynQPanderaDataFrameModel):
    """
    Schema for hr2d__Leave__c entity GET operations.
    Represents leave records in HR2Day system.
    """

    # Standard Salesforce fields
    id: Series[str] = pa.Field(alias="Id", description="Record ID", coerce=True)
    name: Series[str] = pa.Field(alias="Name", description="Leave record", coerce=True)
    created_by_id: Series[str] = pa.Field(alias="CreatedById", description="Created By ID", coerce=True)
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", description="Created Date", coerce=True)
    last_activity_date: Optional[Series[datetime]] = pa.Field(alias="LastActivityDate", nullable=True, coerce=True, description="Last Activity Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", description="Last Modified By ID", coerce=True)
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", description="Last Modified Date", coerce=True)
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", description="System Modstamp", coerce=True)

    # Custom fields
    collective: Optional[Series[bool]] = pa.Field(alias="hr2d__Annual__c", nullable=True, description="Collective", coerce=True)
    approver: Optional[Series[str]] = pa.Field(alias="hr2d__approver1__c", nullable=True, description="Approver", coerce=True)
    approver_original: Optional[Series[str]] = pa.Field(alias="hr2d__Approver1Original__c", nullable=True, description="Approver original", coerce=True)
    employment_sequence_number: Optional[Series[float]] = pa.Field(alias="hr2d__ArbrelVolgnr__c", nullable=True, description="Employment sequence number", coerce=True)
    calculated_hours: Optional[Series[float]] = pa.Field(alias="hr2d__CalculatedHours__c", nullable=True, description="Calculated number of hours", coerce=True)
    calculated_hours_per_day: Optional[Series[str]] = pa.Field(alias="hr2d__CalculatedHoursPerDay__c", nullable=True, description="Calculated number of hours per day", coerce=True)
    calendar_days: Optional[Series[float]] = pa.Field(alias="hr2d__CalendarDays__c", nullable=True, description="Calendar days", coerce=True)
    changes: Optional[Series[str]] = pa.Field(alias="hr2d__Changes__c", nullable=True, description="Changes", coerce=True)
    custom_hours_per_day: Optional[Series[str]] = pa.Field(alias="hr2d__CustomHoursPerDay__c", nullable=True, description="Custom number of hours per day", coerce=True)
    description: Optional[Series[str]] = pa.Field(alias="hr2d__Description__c", nullable=True, description="Explanation", coerce=True)
    details: Optional[Series[str]] = pa.Field(alias="hr2d__Details__c", nullable=True, description="Reference", coerce=True)
    employee: Optional[Series[str]] = pa.Field(alias="hr2d__Employee__c", nullable=True, description="Employee", coerce=True)
    end_date: Optional[Series[date]] = pa.Field(alias="hr2d__EndDate__c", nullable=True, description="End date", coerce=True)
    external_key: Optional[Series[str]] = pa.Field(alias="hr2d__ExternalKey__c", nullable=True, description="External key", coerce=True)
    force_workflow: Optional[Series[bool]] = pa.Field(alias="hr2d__ForceWorkflow__c", nullable=True, description="Force workflow", coerce=True)
    hours: Optional[Series[float]] = pa.Field(alias="hr2d__Hours__c", nullable=True, description="Number of hours", coerce=True)
    hours_per_day: Optional[Series[str]] = pa.Field(alias="hr2d__HoursPerDay__c", nullable=True, description="Number of hours per day", coerce=True)
    leave_type: Optional[Series[str]] = pa.Field(alias="hr2d__Leave__c", nullable=True, description="Type of leave", coerce=True)
    leave_code: Optional[Series[str]] = pa.Field(alias="hr2d__LeaveCode__c", nullable=True, description="Leave code", coerce=True)
    leave_distribution: Optional[Series[str]] = pa.Field(alias="hr2d__LeaveDistribution__c", nullable=True, description="Leave distribution", coerce=True)
    leave_entitlement: Optional[Series[str]] = pa.Field(alias="hr2d__LeaveEntitlement__c", nullable=True, description="Leave entitlements", coerce=True)
    leave_until: Optional[Series[date]] = pa.Field(alias="hr2d__LeaveTodayUntil__c", nullable=True, description="Leave until", coerce=True)
    reason: Optional[Series[str]] = pa.Field(alias="hr2d__Reason__c", nullable=True, description="Reason", coerce=True)
    start_date: Optional[Series[date]] = pa.Field(alias="hr2d__StartDate__c", nullable=True, description="Start date", coerce=True)
    time_in_lieu_type: Optional[Series[str]] = pa.Field(alias="hr2d__TvtType__c", nullable=True, description="Time in lieu type", coerce=True)
    workflow_status: Optional[Series[str]] = pa.Field(alias="hr2d__Workflowstatus__c", nullable=True, description="Workflow status", coerce=True)

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
            },
            "approver": {
                "parent_schema": "EmployeeGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "approver_original": {
                "parent_schema": "EmployeeGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "leave_entitlement": {
                "parent_schema": "LeaveEntitlementGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }
