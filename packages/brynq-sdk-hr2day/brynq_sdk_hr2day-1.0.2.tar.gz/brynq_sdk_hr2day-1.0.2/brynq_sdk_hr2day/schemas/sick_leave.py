from typing import Optional
from datetime import date, datetime
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class SickLeaveGet(BrynQPanderaDataFrameModel):
    """
    Schema for hr2d__SickLeave__c entity GET operations.
    Represents sick leave records in HR2Day system.
    """

    # Standard Salesforce fields
    id: Series[str] = pa.Field(alias="Id", description="Record ID", coerce=True)
    name: Series[str] = pa.Field(alias="Name", description="Sick leave record", coerce=True)
    created_by_id: Series[str] = pa.Field(alias="CreatedById", description="Created By ID", coerce=True)
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", description="Created Date", coerce=True)
    last_activity_date: Optional[Series[datetime]] = pa.Field(alias="LastActivityDate", nullable=True, coerce=True, description="Last Activity Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", description="Last Modified By ID", coerce=True)
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", description="Last Modified Date", coerce=True)
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", description="System Modstamp", coerce=True)

    # Custom fields
    actual_due_date: Optional[Series[date]] = pa.Field(alias="hr2d__ActualDueDate__c", nullable=True, description="Actual date of delivery", coerce=True)
    employment_sequence_number: Optional[Series[float]] = pa.Field(nullable=True, alias="hr2d__ArbrelVolgnr__c", description="Employment sequence number", coerce=True)
    calendar_days: Optional[Series[float]] = pa.Field(alias="hr2d__CalendarDays__c", nullable=True, description="Calendar days from start date", coerce=True)
    calendar_days_related: Optional[Series[float]] = pa.Field(alias="hr2d__CalendarDaysRelated__c", nullable=True, description="Calendar days", coerce=True)
    calendar_days_related_net: Optional[Series[float]] = pa.Field(alias="hr2d__CalendarDaysRelatedNet__c", nullable=True, description="Net calendar days", coerce=True)
    case_manager: Optional[Series[str]] = pa.Field(alias="hr2d__CaseManager__c", nullable=True, description="Case manager", coerce=True)
    case_manager2: Optional[Series[str]] = pa.Field(alias="hr2d__CaseManager2__c", nullable=True, description="Case manager 2", coerce=True)
    case_manager2_original: Optional[Series[str]] = pa.Field(alias="hr2d__CaseManager2Original__c", nullable=True, description="Case manager 2 original", coerce=True)
    case_manager3: Optional[Series[str]] = pa.Field(alias="hr2d__CaseManager3__c", nullable=True, description="Case manager 3", coerce=True)
    case_manager3_original: Optional[Series[str]] = pa.Field(alias="hr2d__CaseManager3Original__c", nullable=True, description="Case manager 3 original", coerce=True)
    case_manager_group_id: Optional[Series[str]] = pa.Field(alias="hr2d__CaseManagerGroupId__c", nullable=True, description="Case manager group ID", coerce=True)
    case_manager_group_name: Optional[Series[str]] = pa.Field(alias="hr2d__CaseManagerGroupName__c", nullable=True, description="Case manager group name", coerce=True)
    case_manager_original: Optional[Series[str]] = pa.Field(alias="hr2d__CaseManagerOriginal__c", nullable=True, description="Case manager original", coerce=True)
    case_manager_user: Optional[Series[str]] = pa.Field(alias="hr2d__CaseManagerUser__c", nullable=True, description="Case manager user", coerce=True)
    classification: Optional[Series[str]] = pa.Field(alias="hr2d__Classification__c", nullable=True, description="Sick leave classification standard options", coerce=True)
    classification_picked: Optional[Series[str]] = pa.Field(alias="hr2d__ClassificationPicked__c", nullable=True, description="Classification", coerce=True)
    connector_sequence_number: Optional[Series[float]] = pa.Field(alias="hr2d__ConnectorSequenceNumber__c", nullable=True, description="Sick leave notification sequence number", coerce=True)
    date_related_case: Optional[Series[date]] = pa.Field(alias="hr2d__DateRelatedCase__c", nullable=True, description="Date of first sick leave", coerce=True)
    part_time_factor_assignment: Optional[Series[float]] = pa.Field(alias="hr2d__DeeltijdFactorArbrel__c", nullable=True, description="Part-time factor assignment", coerce=True)
    department: Optional[Series[str]] = pa.Field(alias="hr2d__Department__c", nullable=True, description="Department", coerce=True)
    details: Optional[Series[str]] = pa.Field(alias="hr2d__Details__c", nullable=True, description="Details", coerce=True)
    employee: Optional[Series[str]] = pa.Field(alias="hr2d__Employee__c", nullable=True, description="Employee", coerce=True)
    end_date: Optional[Series[date]] = pa.Field(alias="hr2d__EndDate__c", nullable=True, description="End date", coerce=True)
    end_date_filter: Optional[Series[date]] = pa.Field(alias="hr2d__EndDateFilter__c", nullable=True, description="End date (filterfield)", coerce=True)
    expected_due_date: Optional[Series[date]] = pa.Field(alias="hr2d__ExpectedDueDate__c", nullable=True, description="Expected due date", coerce=True)
    expected_end_date: Optional[Series[date]] = pa.Field(alias="hr2d__ExpectedEndDate__c", nullable=True, description="Expected end date", coerce=True)
    external_key: Optional[Series[str]] = pa.Field(alias="hr2d__ExternalKey__c", nullable=True, description="External key", coerce=True)
    hours_first_day: Optional[Series[float]] = pa.Field(alias="hr2d__HoursFirstDay__c", nullable=True, description="Different number of hours absent first day", coerce=True)
    key: Optional[Series[str]] = pa.Field(alias="hr2d__Key__c", nullable=True, description="Key", coerce=True)
    nursing_address: Optional[Series[bool]] = pa.Field(alias="hr2d__NursingAddress__c", nullable=True, description="Different nursing address", coerce=True)
    nursing_address_desc: Optional[Series[str]] = pa.Field(alias="hr2d__NursingAddressDesc__c", nullable=True, description="Nursing address description", coerce=True)
    nursing_city: Optional[Series[str]] = pa.Field(alias="hr2d__NursingCity__c", nullable=True, description="City", coerce=True)
    nursing_country: Optional[Series[str]] = pa.Field(alias="hr2d__NursingCountry__c", nullable=True, description="Country", coerce=True)
    nursing_house_number: Optional[Series[float]] = pa.Field(alias="hr2d__NursingHouseNr__c", nullable=True, description="House number", coerce=True)
    nursing_house_number_addition: Optional[Series[str]] = pa.Field(alias="hr2d__NursingHouseNrAdd__c", nullable=True, description="House number addition", coerce=True)
    nursing_postal_code: Optional[Series[str]] = pa.Field(alias="hr2d__NursingPostalCode__c", nullable=True, description="Postal code", coerce=True)
    nursing_street: Optional[Series[str]] = pa.Field(alias="hr2d__NursingStreet__c", nullable=True, description="Street", coerce=True)
    pay_comment: Optional[Series[str]] = pa.Field(alias="hr2d__PayComment__c", nullable=True, description="Notes on continued payment", coerce=True)
    pay_end: Optional[Series[date]] = pa.Field(alias="hr2d__PayEnd__c", nullable=True, description="End of continued payment", coerce=True)
    pay_wait_days: Optional[Series[float]] = pa.Field(alias="hr2d__PayWaitDays__c", nullable=True, description="Waiting days", coerce=True)
    pp1_perc: Optional[Series[float]] = pa.Field(alias="hr2d__PP1_Perc__c", nullable=True, description="Cont. payment 1st period", coerce=True)
    pp2_perc: Optional[Series[float]] = pa.Field(alias="hr2d__PP2_Perc__c", nullable=True, description="Cont. payment 2nd period", coerce=True)
    pp2_start: Optional[Series[date]] = pa.Field(alias="hr2d__PP2_Start__c", nullable=True, description="Start 2nd period", coerce=True)
    pp3_perc: Optional[Series[float]] = pa.Field(alias="hr2d__PP3_Perc__c", nullable=True, description="Cont. payment 3rd period", coerce=True)
    pp3_start: Optional[Series[date]] = pa.Field(alias="hr2d__PP3_Start__c", nullable=True, description="Start 3rd period", coerce=True)
    pp4_perc: Optional[Series[float]] = pa.Field(alias="hr2d__PP4_Perc__c", nullable=True, description="Cont. payment 4rd period", coerce=True)
    pp4_start: Optional[Series[date]] = pa.Field(alias="hr2d__PP4_Start__c", nullable=True, description="Start 4th period", coerce=True)
    record_id: Optional[Series[str]] = pa.Field(alias="hr2d__RecordId__c", nullable=True, description="Record ID (long)", coerce=True)
    right_of_recourse: Optional[Series[bool]] = pa.Field(alias="hr2d__RightOfRecourse__c", nullable=True, description="Possibility of recourse", coerce=True)
    sick_classification: Optional[Series[str]] = pa.Field(alias="hr2d__SickClassification__c", nullable=True, description="Sick leave classification", coerce=True)
    sick_perc_today: Optional[Series[float]] = pa.Field(alias="hr2d__SickPercToday__c", nullable=True, description="Percentage sickleave today", coerce=True)
    start_date: Optional[Series[date]] = pa.Field(alias="hr2d__StartDate__c", nullable=True, description="Start date", coerce=True)
    start_date_tasks: Optional[Series[date]] = pa.Field(alias="hr2d__StartDateTasks__c", nullable=True, description="Start date for the tasks", coerce=True)

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
            "department": {
                "parent_schema": "DepartmentGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "sick_classification": {
                "parent_schema": "SickClassificationGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "case_manager": {
                "parent_schema": "EmployeeGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "case_manager2": {
                "parent_schema": "EmployeeGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "case_manager3": {
                "parent_schema": "EmployeeGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }
