from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator
from pandera.typing import Series
import pandera as pa

from brynq_sdk_functions import BrynQPanderaDataFrameModel

class CostCenterUpdateFields(BaseModel):
    """Fields that can be updated for a cost center"""
    name: Optional[str] = Field(alias="Name", default=None, description="Name of the cost center")
    start_date: Optional[date] = Field(alias="hr2d__StartDate__c", default=None, description="Start date of the cost center")
    end_date: Optional[date] = Field(alias="hr2d__EndDate__c", default=None, description="End date of the cost center")
    description: Optional[str] = Field(alias="hr2d__Description__c", default=None, description="Description of the cost center")
    dimension: Optional[str] = Field(alias="hr2d__Dimension__c", default=None, description="Dimension of the cost center")
    classification: Optional[str] = Field(alias="hr2d__Classification__c", default=None, description="Classification of the cost center")
    recap_char: Optional[str] = Field(alias="hr2d__RecapChar__c", default=None, description="Verdichtings-kenmerk of the cost center")

    class Config:
        """Schema configuration"""
        populate_by_name = True


class CostCenterUpdate(BaseModel):
    """Schema for updating cost center data"""
    # Identification fields
    cost_center_id: Optional[str] = Field(alias="costcenterId", default=None, description="Cost center ID for update operations")
    employer_id: Optional[str] = Field(alias="employerId", default=None, description="Employer ID for insert operations")
    employer_name: Optional[str] = Field(alias="employerName", default=None, description="Employer name for insert operations")
    employer_tax_id: Optional[str] = Field(alias="employerTaxId", default=None, description="Employer tax ID for insert operations")

    # Cost center fields
    costcenter: CostCenterUpdateFields = Field(description="Fields to update")

    @model_validator(mode='after')
    def validate_identification_fields(self) -> 'CostCenterUpdate':
        """Validate that either cost_center_id or one of the employer identification fields is provided."""
        if not self.cost_center_id and not self.employer_id and not self.employer_name and not self.employer_tax_id:
            raise ValueError("Either cost_center_id or one of employer_id, employer_name, employer_tax_id must be provided")
        return self

    @model_validator(mode='after')
    def validate_name_for_insert(self) -> 'CostCenterUpdate':
        """Validate that Name is provided for insert operations."""
        if not self.cost_center_id and not self.costcenter.name:
            raise ValueError("Name is required for insert operations")
        return self

    class Config:
        """Schema configuration"""
        populate_by_name = True

class CostCenterGet(BrynQPanderaDataFrameModel):
    """Schema for hr2d__CostCenter__c entity in HR2Day. Represents a cost center record."""

    # Salesforce Standard Fields
    id: Series[str] = pa.Field(alias="Id", nullable=True, coerce=True, description="Record ID")
    name: Series[str] = pa.Field(alias="Name", nullable=True, coerce=True, description="Name/Code")
    created_by_id: Series[str] = pa.Field(alias="CreatedById", nullable=True, coerce=True, description="Created By ID")
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", nullable=True, coerce=True, description="Created Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", nullable=True, coerce=True, description="Last Modified By ID")
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", nullable=True, coerce=True, description="Last Modified Date")
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", nullable=True, coerce=True, description="System Modstamp")

    # HR2Day Custom Fields
    classification: Series[str] = pa.Field(alias="hr2d__Classification__c", nullable=True, coerce=True, description="Rubricering")
    delegate: Series[str] = pa.Field(alias="hr2d__Delegate__c", nullable=True, coerce=True, description="Gedelegeerd budgethouder")
    department: Series[str] = pa.Field(alias="hr2d__Department__c", nullable=True, coerce=True, description="Afdeling")
    description: Series[str] = pa.Field(alias="hr2d__Description__c", nullable=True, coerce=True, description="Omschrijving kostenplaats")
    dimension: Series[str] = pa.Field(alias="hr2d__Dimension__c", nullable=True, coerce=True, description="Dimensie")
    employer: Series[str] = pa.Field(alias="hr2d__Employer__c", nullable=True, coerce=True, description="Werkgever")
    end_date: Series[datetime] = pa.Field(alias="hr2d__EndDate__c", nullable=True, coerce=True, description="Laatste dag waarop de kostenplaats geldig is")
    key: Series[str] = pa.Field(alias="hr2d__Key__c", nullable=True, coerce=True, description="Sleutelveld kostenplaats")
    main_cost_center: Series[bool] = pa.Field(alias="hr2d__MainCostCenter__c", nullable=True, coerce=True, description="Hoofdkostenplaats")
    manager: Series[str] = pa.Field(alias="hr2d__Manager__c", nullable=True, coerce=True, description="Eigenaar (budgethouder) van de kostenplaats")
    recap_char: Series[str] = pa.Field(alias="hr2d__RecapChar__c", nullable=True, coerce=True, description="Kenmerk waarop kostenplaats kan worden verdicht")
    record_id: Series[str] = pa.Field(alias="hr2d__RecordId__c", nullable=True, coerce=True, description="Case insensitive id (18 karakters) van dit record")
    start_date: Series[datetime] = pa.Field(alias="hr2d__StartDate__c", nullable=True, coerce=True, description="Eerste dag waarop de kostenplaats geldig is")

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
