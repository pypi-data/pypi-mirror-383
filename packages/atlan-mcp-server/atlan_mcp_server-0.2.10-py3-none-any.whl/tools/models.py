from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class CertificateStatus(str, Enum):
    """Enum for allowed certificate status values."""

    VERIFIED = "VERIFIED"
    DRAFT = "DRAFT"
    DEPRECATED = "DEPRECATED"


class UpdatableAttribute(str, Enum):
    """Enum for attributes that can be updated."""

    USER_DESCRIPTION = "user_description"
    CERTIFICATE_STATUS = "certificate_status"
    README = "readme"
    TERM = "term"


class TermOperation(str, Enum):
    """Enum for term operations on assets."""

    APPEND = "append"
    REPLACE = "replace"
    REMOVE = "remove"


class TermOperations(BaseModel):
    """Model for term operations on assets."""

    operation: TermOperation
    term_guids: List[str]


class UpdatableAsset(BaseModel):
    """Class representing an asset that can be updated."""

    guid: str
    name: str
    qualified_name: str
    type_name: str
    user_description: Optional[str] = None
    certificate_status: Optional[CertificateStatus] = None
    glossary_guid: Optional[str] = None


class Glossary(BaseModel):
    """Payload model for creating a glossary asset."""

    name: str
    user_description: Optional[str] = None
    certificate_status: Optional[CertificateStatus] = None


class GlossaryCategory(BaseModel):
    """Payload model for creating a glossary category asset."""

    name: str
    glossary_guid: str
    user_description: Optional[str] = None
    certificate_status: Optional[CertificateStatus] = None
    parent_category_guid: Optional[str] = None


class GlossaryTerm(BaseModel):
    """Payload model for creating a glossary term asset."""

    name: str
    glossary_guid: str
    user_description: Optional[str] = None
    certificate_status: Optional[CertificateStatus] = None
    category_guids: Optional[List[str]] = None
