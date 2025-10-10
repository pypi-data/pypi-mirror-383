from datetime import datetime
from pandera.typing import Series
import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class DepartmentDetailsGet(BrynQPanderaDataFrameModel):
    """Schema for hr2d__DepartmentDetails__c entity in HR2Day. Represents department details record."""

    # Salesforce Standard Fields
    id: Series[str] = pa.Field(alias="Id", nullable=True, coerce=True, description="Record ID")
    name: Series[str] = pa.Field(alias="Name", nullable=True, coerce=True, description="Department details name")
    created_by_id: Series[str] = pa.Field(alias="CreatedById", nullable=True, coerce=True, description="Created By ID")
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", nullable=True, coerce=True, description="Created Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", nullable=True, coerce=True, description="Last Modified By ID")
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", nullable=True, coerce=True, description="Last Modified Date")
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", nullable=True, coerce=True, description="System Modstamp")

    # HR2Day Custom Fields
    cost_center: Series[str] = pa.Field(alias="hr2d__CostCenter__c", nullable=True, coerce=True, description="Kostenplaats")
    cost_center_dim2: Series[str] = pa.Field(alias="hr2d__CostCenter_Dim2__c", nullable=True, coerce=True, description="Kostenplaats dimensie 2")
    cost_center_dim3: Series[str] = pa.Field(alias="hr2d__CostCenter_Dim3__c", nullable=True, coerce=True, description="Kostenplaats dimensie 3")
    department: Series[str] = pa.Field(alias="hr2d__Department__c", nullable=True, coerce=True, description="Afdeling waar dit een detail van is")
    employer: Series[str] = pa.Field(alias="hr2d__Employer__c", nullable=True, coerce=True, description="Werkgever waarvoor deze details van toepassing zijn")
    end_date: Series[datetime] = pa.Field(alias="hr2d__EndDate__c", nullable=True, coerce=True, description="Laatste dag waarop deze instellingen geldig zijn")
    field_name: Series[str] = pa.Field(alias="hr2d__FieldName__c", nullable=True, coerce=True, description="Veldnaam")
    field_name2: Series[str] = pa.Field(alias="hr2d__FieldName2__c", nullable=True, coerce=True, description="Veldnaam 2")
    field_name3: Series[str] = pa.Field(alias="hr2d__FieldName3__c", nullable=True, coerce=True, description="Veldnaam 3")
    field_value: Series[str] = pa.Field(alias="hr2d__FieldValue__c", nullable=True, coerce=True, description="Veldwaarde")
    field_value2: Series[str] = pa.Field(alias="hr2d__FieldValue2__c", nullable=True, coerce=True, description="Veldwaarde 2")
    field_value3: Series[str] = pa.Field(alias="hr2d__FieldValue3__c", nullable=True, coerce=True, description="Veldwaarde 3")
    start_date: Series[datetime] = pa.Field(alias="hr2d__StartDate__c", nullable=True, coerce=True, description="Eerste dag waarop deze gegevens geldig zijn")

    class _Annotation:
        """Annotation class for primary and foreign keys"""
        primary_key = "id"
        foreign_keys = {
            "employer": {
                "parent_schema": "EmployerGet",
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

    class Config:
        """Schema configuration"""
        strict = "filter"  # Allow extra columns not defined in schema
        coerce = True
        add_missing_columns = True  # Add missing columns as nullable
