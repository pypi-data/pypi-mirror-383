from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class FileContentResponse(BaseModel):
    """Schema for the response from the RestFileContent API."""
    request_id: Optional[str] = Field(None, alias="requestId", description="Logging ID (not yet implemented)", coerce=True)
    requester_id: str = Field(..., alias="requesterId", description="The requesterId used for the API call", coerce=True)
    errors: Optional[str] = Field(None, description="Errors, empty if there are no errors", coerce=True)
    content_version_id: Optional[str] = Field(None, alias="contentVersionId", description="ID of the created file if upload was successful", coerce=True)

    class Config:
        """Pydantic configuration"""
        coerce = True
        strict = False
        populate_by_name = True


class FileMetadata(BaseModel):
    """Schema for file metadata in HR2Day API."""
    document_category: Optional[Literal["Bedrijfsmiddel", "Beoordeling", "Declaratie", "Opleiding", "Salarisspecificatie", "Verlof", "Vervangingen", "Verzuim", "Overig"]] = Field(None, alias="hr2d__DocumentCategory__c", description="Document category (HR2day option value)")
    original_created_date: Optional[datetime] = Field(None, alias="hr2d__OriginalRecordCreatedDate__c", description="Original creation date of the file", coerce=True)
    external_key: Optional[str] = Field(None, alias="hr2d__Key__c", description="External reference key for the file", coerce=True)
    limited_access: Optional[bool] = Field(None, alias="hr2d__limitedAccess__c", description="Indicates if document is only displayed for certain document profiles", coerce=True)
    allowed_document_profiles: Optional[str] = Field(None, alias="hr2d__AllowedDocumentProfiles__c", description="Names of document profiles with access, separated by ~", coerce=True)

    class Config:
        """Pydantic configuration"""
        coerce = True
        strict = False
        populate_by_name = True


class FileMetadataRequest(BaseModel):
    """Schema for file metadata request in HR2Day API."""
    requester_id: str = Field(..., alias="requesterId", description="Requester ID provided by HR2Day", coerce=True)
    content_version_id: str = Field(..., alias="contentVersionId", description="ID of the file content from FileContent upload", coerce=True)
    employer: Optional[str] = Field(None, description="Employer name (mandatory except for keyType EMPLOYEEID)", coerce=True)
    key_type: Literal["EMPLOYEEID", "BSN", "EMPLOYEENR", "EMPLOYEENRALTERNATIVE", "EMPLOYEEKEY"] = Field(..., alias="keyType", description="Type of key used to identify the employee", coerce=True)
    key_value: str = Field(..., alias="keyValue", description="Value of the field selected by keyType", coerce=True)
    document_profile_mode: Optional[Literal["MEDEWERKER", "STANDAARDPROFIEL"]] = Field(None, alias="documentProfileMode", description="Document profile mode", coerce=True)
    alternative_owner_id: Optional[str] = Field(None, alias="alternativeOwnerId", description="Specific user ID who becomes the owner of the file", coerce=True)
    file: FileMetadata = Field(..., description="File metadata")

    @model_validator(mode='after')
    def validate_employer(self):
        """Validate that employer is provided when keyType is not EMPLOYEEID."""
        if self.key_type != "EMPLOYEEID" and not self.employer:
            raise ValueError("Employer is mandatory when keyType is not EMPLOYEEID")
        return self

    class Config:
        """Pydantic configuration"""
        coerce = True
        strict = False
        populate_by_name = True


class FileMetadataResponse(BaseModel):
    """Schema for the response from the RestFile API."""
    request_id: Optional[str] = Field(None, alias="requestId", description="Logging ID (not yet implemented)", coerce=True)
    requester_id: str = Field(..., alias="requesterId", description="The requesterId used for the API call", coerce=True)
    errors: Optional[str] = Field(None, description="Errors, empty if there are no errors", coerce=True)
    file_id: Optional[str] = Field(None, alias="fileId", description="ID of the created file if metadata was successfully processed", coerce=True)

    class Config:
        """Pydantic configuration"""
        coerce = True
        strict = False
        populate_by_name = True


class FileGet(BaseModel):
    """Schema for hr2d__File__c entity in HR2Day. Represents a file record."""

    # File specific fields
    document_category: Optional[str] = Field(None, alias="hr2d__DocumentCategory__c", description="Document category", coerce=True)
    original_created_date: Optional[datetime] = Field(None, alias="hr2d__OriginalRecordCreatedDate__c", description="Original creation date", coerce=True)
    external_key: Optional[str] = Field(None, alias="hr2d__Key__c", description="External reference key", coerce=True)
    employee: Optional[str] = Field(None, alias="hr2d__Employee__c", description="Employee ID the file is linked to", coerce=True)
    limited_access: Optional[bool] = Field(None, alias="hr2d__limitedAccess__c", description="Limited access flag", coerce=True)
    allowed_document_profiles: Optional[str] = Field(None, alias="hr2d__AllowedDocumentProfiles__c", description="Allowed document profiles", coerce=True)

    class Config:
        """Pydantic configuration"""
        coerce = True
        strict = False
        populate_by_name = True
