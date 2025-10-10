from typing import Optional
from datetime import date, datetime
from pandera.typing import Series
import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class WageComponentOutputGet(BrynQPanderaDataFrameModel):
    """
    Schema for hr2d__Looncompoutput__c entity GET operations.
    Represents wage component output records in HR2Day system.
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
    cumulative: Optional[Series[float]] = pa.Field(alias="hr2d__Cumulatief__c", nullable=True, description="Cumulative", coerce=True)
    date: Optional[Series[date]] = pa.Field(alias="hr2d__Datum__c", nullable=True, description="Date", coerce=True)
    declaration: Optional[Series[str]] = pa.Field(alias="hr2d__Declaration__c", nullable=True, description="Declaration", coerce=True)
    department: Optional[Series[str]] = pa.Field(alias="hr2d__Department__c", nullable=True, description="Department", coerce=True)
    end_date: Optional[Series[date]] = pa.Field(alias="hr2d__EndDate__c", nullable=True, description="End date", coerce=True)
    factor: Optional[Series[float]] = pa.Field(alias="hr2d__Factor__c", nullable=True, description="Factor", coerce=True)
    origin: Optional[Series[str]] = pa.Field(alias="hr2d__Herkomst__c", nullable=True, description="Origin", coerce=True)
    import_id: Optional[Series[str]] = pa.Field(alias="hr2d__ImportId__c", nullable=True, description="Import ID", coerce=True)
    import_key: Optional[Series[str]] = pa.Field(alias="hr2d__ImportKey__c", nullable=True, description="Import key", coerce=True)
    index: Optional[Series[float]] = pa.Field(alias="hr2d__Index__c", nullable=True, description="Index", coerce=True)
    job: Optional[Series[str]] = pa.Field(alias="hr2d__Job__c", nullable=True, description="Job", coerce=True)
    original_wage_component_employment: Optional[Series[str]] = pa.Field(alias="hr2d__LooncompArbrel__c", nullable=True, description="Original wage component (employment)", coerce=True)
    wage_component: Optional[Series[str]] = pa.Field(alias="hr2d__Looncomponent__c", nullable=True, description="Wage component definition", coerce=True)
    old_wage_component: Optional[Series[str]] = pa.Field(alias="hr2d__LooncompOud__c", nullable=True, description="Old wage component (in case of change)", coerce=True)
    wage_component_output_change: Optional[Series[str]] = pa.Field(alias="hr2d__LooncompOutputChange__c", nullable=True, description="Wage component change (output)", coerce=True)
    payslip: Optional[Series[str]] = pa.Field(alias="hr2d__Loonstrook__c", nullable=True, description="Payslip", coerce=True)
    prorata_factor: Optional[Series[float]] = pa.Field(alias="hr2d__ProrataFactor__c", nullable=True, description="Prorata factor", coerce=True)
    reason: Optional[Series[str]] = pa.Field(alias="hr2d__Reden__c", nullable=True, description="Reason", coerce=True)
    reference: Optional[Series[str]] = pa.Field(alias="hr2d__Referentie__c", nullable=True, description="Reference", coerce=True)
    scheme: Optional[Series[str]] = pa.Field(alias="hr2d__Regeling__c", nullable=True, description="Scheme", coerce=True)
    substitution: Optional[Series[str]] = pa.Field(alias="hr2d__Substitution__c", nullable=True, description="Substitution", coerce=True)
    rate: Optional[Series[float]] = pa.Field(alias="hr2d__Tarief__c", nullable=True, description="Rate", coerce=True)
    payroll: Optional[Series[str]] = pa.Field(alias="hr2d__Verloning__c", nullable=True, description="Payroll", coerce=True)
    substitution_old: Optional[Series[str]] = pa.Field(alias="hr2d__Vervanging__c", nullable=True, description="Substitution (old)", coerce=True)
    sequence_number: Optional[Series[float]] = pa.Field(alias="hr2d__Volgnr__c", nullable=True, description="Sequence number", coerce=True)
    changes: Optional[Series[str]] = pa.Field(alias="hr2d__Wijzigingen__c", nullable=True, description="Changes", coerce=True)

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
            "substitution": {
                "parent_schema": "SubstitutionGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "payroll": {
                "parent_schema": "PayrollGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }
