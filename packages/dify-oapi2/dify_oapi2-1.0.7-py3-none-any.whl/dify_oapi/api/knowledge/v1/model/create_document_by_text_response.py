"""Create document by text response model."""

from dify_oapi.core.model.base_response import BaseResponse

from .document_info import DocumentInfo


class CreateDocumentByTextResponse(BaseResponse):
    """Response model for create document by text API."""

    document: DocumentInfo | None = None
    batch: str | None = None
