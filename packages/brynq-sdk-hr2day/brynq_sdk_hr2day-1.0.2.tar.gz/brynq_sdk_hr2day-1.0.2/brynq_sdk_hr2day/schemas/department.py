from datetime import datetime
from pandera.typing import Series
import pandera as pa

from brynq_sdk_functions import BrynQPanderaDataFrameModel


class DepartmentGet(BrynQPanderaDataFrameModel):
    """Schema for hr2d__Department__c entity GET operations in HR2Day. Represents a department record."""

    # Base Salesforce fields
    id: Series[str] = pa.Field(alias="Id", nullable=True, description="Record ID", coerce=True)
    is_deleted: Series[bool] = pa.Field(alias="IsDeleted", nullable=True, description="Is deleted flag", coerce=True)
    name: Series[str] = pa.Field(alias="Name", nullable=True, description="Name of the record", coerce=True)
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", nullable=True, description="Created date", coerce=True)
    created_by_id: Series[str] = pa.Field(alias="CreatedById", nullable=True, description="Created by ID", coerce=True)
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", nullable=True, description="Last modified date", coerce=True)
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", nullable=True, description="Last modified by ID", coerce=True)
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", nullable=True, description="System modstamp", coerce=True)

    # HR2Day Custom Fields
    address: Series[str] = pa.Field(alias="hr2d__Address__c", nullable=True, coerce=True, description="Straat Huisnummer Toevoeging")
    city: Series[str] = pa.Field(alias="hr2d__City__c", nullable=True, coerce=True, description="City")
    cost_center: Series[str] = pa.Field(alias="hr2d__CostCenter__c", nullable=True, coerce=True, description="Standaard kostenplaats van deze afdeling")
    delegate: Series[str] = pa.Field(alias="hr2d__Delegate__c", nullable=True, coerce=True, description="Gedelegeerd manager van de afdeling")
    dept_nr: Series[str] = pa.Field(alias="hr2d__DeptNr__c", nullable=True, coerce=True, description="Department nr")
    description: Series[str] = pa.Field(alias="hr2d__Description__c", nullable=True, coerce=True, description="Eventuele omschrijving (volledige naam) van de afdeling")
    description_en: Series[str] = pa.Field(alias="hr2d__Description_EN__c", nullable=True, coerce=True, description="Eventuele omschrijving (volledige naam) van de afdeling (Engels)")
    email: Series[str] = pa.Field(alias="hr2d__Email__c", nullable=True, coerce=True, description="Email")
    employer: Series[str] = pa.Field(alias="hr2d__Employer__c", nullable=True, coerce=True, description="Werkgever waar deze afdeling deel van uitmaakt")
    end_date: Series[datetime] = pa.Field(alias="hr2d__EndDate__c", nullable=True, coerce=True, description="Laatste dag waarop de afdeling geldig is")
    house_nr: Series[float] = pa.Field(alias="hr2d__HouseNr__c", nullable=True, coerce=True, description="House number")
    house_nr_add: Series[str] = pa.Field(alias="hr2d__HouseNrAdd__c", nullable=True, coerce=True, description="House number add.")
    key: Series[str] = pa.Field(alias="hr2d__Key__c", nullable=True, coerce=True, description="Sleutelveld afdeling bestaande uit loonheffingennummer werkgever en naam van de afdeling")
    logo: Series[str] = pa.Field(alias="hr2d__Logo__c", nullable=True, coerce=True, description="Logo")
    logo_id: Series[str] = pa.Field(alias="hr2d__LogoID__c", nullable=True, coerce=True, description="LogoID")
    manager: Series[str] = pa.Field(alias="hr2d__Manager__c", nullable=True, coerce=True, description="Manager van de afdeling")
    name_en: Series[str] = pa.Field(alias="hr2d__Name_EN__c", nullable=True, coerce=True, description="De Engelse naam voor de afdeling")
    parent_dept: Series[str] = pa.Field(alias="hr2d__ParentDept__c", nullable=True, coerce=True, description="Afdeling waar deze afdeling onder valt")
    phone: Series[str] = pa.Field(alias="hr2d__Phone__c", nullable=True, coerce=True, description="Phone")
    postal_code: Series[str] = pa.Field(alias="hr2d__PostalCode__c", nullable=True, coerce=True, description="Postal code")
    record_id: Series[str] = pa.Field(alias="hr2d__RecordId__c", nullable=True, coerce=True, description="Case insensitive id (18 karakters) van dit record")
    sign_dept: Series[str] = pa.Field(alias="hr2d__SignDept__c", nullable=True, coerce=True, description="Deze afdeling wordt gebruikt voor het ondertekenen van brieven")
    sign_name: Series[str] = pa.Field(alias="hr2d__SignName__c", nullable=True, coerce=True, description="Deze naam wordt gebruikt bij het ondertekenen van brieven")
    sign_title: Series[str] = pa.Field(alias="hr2d__SignTitle__c", nullable=True, coerce=True, description="Deze titel wordt gebruikt bij het ondertekenen van brieven")
    start_date: Series[datetime] = pa.Field(alias="hr2d__StartDate__c", nullable=True, coerce=True, description="Eerste dag waarop de afdeling geldig is")
    street: Series[str] = pa.Field(alias="hr2d__Street__c", nullable=True, coerce=True, description="Straat")
    website: Series[str] = pa.Field(alias="hr2d__Website__c", nullable=True, coerce=True, description="Website")

    class _Annotation:
        """Primary and foreign key annotations for Department entity"""
        primary_key = "id"
        foreign_keys = {
            "employer": {
                "parent_schema": "EmployerGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "parent_dept": {
                "parent_schema": "DepartmentGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

    class Config:
        """Schema configuration"""
        strict = "filter"  # Allow extra columns not defined in schema
        coerce = True
        add_missing_columns = True  # Add missing columns as nullable
