from datetime import datetime
from pandera.typing import Series
import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class EmploymentConditionsClusterGet(BrynQPanderaDataFrameModel):
    """Schema for hr2d__ArbVoorwCluster__c entity in HR2Day. Represents an employment conditions cluster record."""

    # Salesforce Standard Fields
    id: Series[str] = pa.Field(alias="Id", nullable=False, coerce=True, description="Record ID")
    owner_id: Series[str] = pa.Field(alias="OwnerId", nullable=True, coerce=True, description="Owner ID")
    is_deleted: Series[bool] = pa.Field(alias="IsDeleted", nullable=True, coerce=True, description="Is Deleted")
    name: Series[str] = pa.Field(alias="Name", nullable=False, coerce=True, description="Naam Arb.voorw.cluster")
    created_by_id: Series[str] = pa.Field(alias="CreatedById", nullable=True, coerce=True, description="Created By ID")
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", nullable=True, coerce=True, description="Created Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", nullable=True, coerce=True, description="Last Modified By ID")
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", nullable=True, coerce=True, description="Last Modified Date")
    last_referenced_date: Series[datetime] = pa.Field(alias="LastReferencedDate", nullable=True, coerce=True, description="Last Referenced Date")
    last_viewed_date: Series[datetime] = pa.Field(alias="LastViewedDate", nullable=True, coerce=True, description="Last Viewed Date")
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", nullable=True, coerce=True, description="System Modstamp")

    # HR2Day Custom Fields
    cao_code: Series[str] = pa.Field(alias="hr2d__CAO_code__c", nullable=True, coerce=True, description="CAO code")
    classification: Series[str] = pa.Field(alias="hr2d__Classificatie__c", nullable=True, coerce=True, description="Classification")
    generic: Series[bool] = pa.Field(alias="hr2d__Generiek__c", nullable=True, coerce=True, description="Generic")
    grouping: Series[str] = pa.Field(alias="hr2d__Groepering__c", nullable=True, coerce=True, description="Grouping")
    chart_of_accounts_schema: Series[str] = pa.Field(alias="hr2d__GrootboekRekSchema__c", nullable=True, coerce=True, description="Chart of Accounts Schema")
    key: Series[str] = pa.Field(alias="hr2d__Key__c", nullable=True, coerce=True, description="Key")
    description: Series[str] = pa.Field(alias="hr2d__Omschrijving__c", nullable=True, coerce=True, description="Description")
    record_id: Series[str] = pa.Field(alias="hr2d__RecordId__c", nullable=True, coerce=True, description="Record-id (long)")
    selectable: Series[str] = pa.Field(alias="hr2d__Selecteerbaar__c", nullable=True, coerce=True, description="Selectable")
    status: Series[str] = pa.Field(alias="hr2d__Status__c", nullable=True, coerce=True, description="Status")
    sub_grouping: Series[str] = pa.Field(alias="hr2d__Subgroepering__c", nullable=True, coerce=True, description="Sub Grouping")
    sub_group_name: Series[str] = pa.Field(alias="hr2d__Subgroepnaam__c", nullable=True, coerce=True, description="Sub Group Name")

    class _Annotation:
        """Annotation class for primary and foreign keys"""
        primary_key = "id"
        foreign_keys = {}

    class Config:
        """Schema configuration"""
        strict = "filter"  # Allow extra columns not defined in schema
        coerce = True
        add_missing_columns = True  # Add missing columns as nullable
