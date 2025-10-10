from typing import Optional
from datetime import date, datetime
from pandera.typing import Series
import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class WageComponentDefinitionGet(BrynQPanderaDataFrameModel):
    """
    Schema for hr2d__Looncomponent__c entity GET operations.
    Represents wage component definition records in HR2Day system.
    """

    # Standard Salesforce fields
    id: Series[str] = pa.Field(alias="Id", description="Record ID", coerce=True)
    name: Series[str] = pa.Field(alias="Name", description="Name wage type", coerce=True)
    created_by_id: Series[str] = pa.Field(alias="CreatedById", description="Created By ID", coerce=True)
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", description="Created Date", coerce=True)
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", description="Last Modified By ID", coerce=True)
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", description="Last Modified Date", coerce=True)
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", description="System Modstamp", coerce=True)

    # Custom fields
    number: Optional[Series[float]] = pa.Field(alias="hr2d__Aantal__c", nullable=True, description="Number", coerce=True)
    account: Optional[Series[str]] = pa.Field(alias="hr2d__Account__c", nullable=True, description="Account", coerce=True)
    employment_relationship: Optional[Series[str]] = pa.Field(alias="hr2d__Arbeidsrelatie__c", nullable=True, description="Employment", coerce=True)
    bank: Optional[Series[str]] = pa.Field(alias="hr2d__Bank__c", nullable=True, description="Bank account", coerce=True)
    bank_holder_name: Optional[Series[str]] = pa.Field(alias="hr2d__Bank_naam__c", nullable=True, description="Bank holder name", coerce=True)
    bank_description: Optional[Series[str]] = pa.Field(alias="hr2d__Bank_omschr__c", nullable=True, description="Bank description", coerce=True)
    bank_bic: Optional[Series[str]] = pa.Field(alias="hr2d__BankBIC__c", nullable=True, description="Bank BIC", coerce=True)
    bank_iban: Optional[Series[str]] = pa.Field(alias="hr2d__BankIBAN__c", nullable=True, description="Bank IBAN", coerce=True)
    amount: Optional[Series[float]] = pa.Field(alias="hr2d__Bedrag__c", nullable=True, description="Amount", coerce=True)
    contract_identification: Optional[Series[str]] = pa.Field(alias="hr2d__Contractkenmerk__c", nullable=True, description="Contract identification", coerce=True)
    cost_center: Optional[Series[str]] = pa.Field(alias="hr2d__CostCenter__c", nullable=True, description="Cost center", coerce=True)
    cost_center_dim2: Optional[Series[str]] = pa.Field(alias="hr2d__CostCenter_Dim2__c", nullable=True, description="Cost center Dim2", coerce=True)
    cost_center_dim3: Optional[Series[str]] = pa.Field(alias="hr2d__CostCenter_Dim3__c", nullable=True, description="Cost center Dim3", coerce=True)
    department: Optional[Series[str]] = pa.Field(alias="hr2d__Department__c", nullable=True, description="Department", coerce=True)
    factor: Optional[Series[float]] = pa.Field(alias="hr2d__Factor__c", nullable=True, description="Factor", coerce=True)
    valid_until: Optional[Series[date]] = pa.Field(alias="hr2d__Geldig_tot__c", nullable=True, description="Valid until", coerce=True)
    valid_until_filter: Optional[Series[date]] = pa.Field(alias="hr2d__Geldig_totFilter__c", nullable=True, description="Valid until (filter field)", coerce=True)
    valid_until_in_context: Optional[Series[date]] = pa.Field(alias="hr2d__Geldig_totInContext__c", nullable=True, description="Valid until (in context employment record)", coerce=True)
    valid_from: Optional[Series[date]] = pa.Field(alias="hr2d__Geldig_van__c", nullable=True, description="Valid from", coerce=True)
    valid_from_filter: Optional[Series[date]] = pa.Field(alias="hr2d__Geldig_vanFilter__c", nullable=True, description="Valid from (filter field)", coerce=True)
    valid_from_in_context: Optional[Series[date]] = pa.Field(alias="hr2d__Geldig_vanInContext__c", nullable=True, description="Valid from (in context employment record)", coerce=True)
    origin: Optional[Series[str]] = pa.Field(alias="hr2d__Herkomst__c", nullable=True, description="Origin", coerce=True)
    job: Optional[Series[str]] = pa.Field(alias="hr2d__Job__c", nullable=True, description="Job", coerce=True)
    leave_scheme_booking_period: Optional[Series[str]] = pa.Field(alias="hr2d__LeaveSchemeBookingPeriod__c", nullable=True, description="Leave scheme booking period", coerce=True)
    wage_component: Optional[Series[str]] = pa.Field(alias="hr2d__Looncomponent__c", nullable=True, description="Wage type definition", coerce=True)
    reason: Optional[Series[str]] = pa.Field(alias="hr2d__Reden__c", nullable=True, description="Reason", coerce=True)
    reference: Optional[Series[str]] = pa.Field(alias="hr2d__Referentie__c", nullable=True, description="Reference", coerce=True)
    shift: Optional[Series[str]] = pa.Field(alias="hr2d__Rooster__c", nullable=True, description="Shift", coerce=True)
    rate: Optional[Series[float]] = pa.Field(alias="hr2d__Tarief__c", nullable=True, description="Rate", coerce=True)
    hours_per_week: Optional[Series[float]] = pa.Field(alias="hr2d__UrenWeek__c", nullable=True, description="Hours per week", coerce=True)
    substitutor_of: Optional[Series[str]] = pa.Field(alias="hr2d__VervangerVan__c", nullable=True, description="Substitutor of", coerce=True)
    sequence_number: Optional[Series[float]] = pa.Field(alias="hr2d__Volgnr__c", nullable=True, description="Sequence number", coerce=True)
    previous_wage_type_id: Optional[Series[str]] = pa.Field(alias="hr2d__Vrg_Lncomp_ID__c", nullable=True, description="Previous wage type (ID)", coerce=True)

    class Config:
        """Pandera configuration"""
        strict = "filter"
        add_missing_columns = True
        coerce = True

    class _Annotation:
        """Annotation class for primary and foreign keys"""
        primary_key = "id"
        foreign_keys = {
            "account": {
                "parent_schema": "AccountGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "employment_relationship": {
                "parent_schema": "EmploymentRelationshipGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "cost_center": {
                "parent_schema": "CostCenterGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "department": {
                "parent_schema": "DepartmentGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "job": {
                "parent_schema": "JobGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "wage_component": {
                "parent_schema": "WageComponentDefinitionGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "substitutor_of": {
                "parent_schema": "EmployeeGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }
