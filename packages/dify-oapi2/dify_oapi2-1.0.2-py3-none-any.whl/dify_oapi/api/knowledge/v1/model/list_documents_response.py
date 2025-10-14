"""List documents response model."""

from dify_oapi.core.model.base_response import BaseResponse

from .document_info import DocumentInfo


class ListDocumentsResponse(BaseResponse):
    """Response model for list documents API."""

    data: list[DocumentInfo] | None = None
    has_more: bool | None = None
    limit: int | None = None
    total: int | None = None
    page: int | None = None
