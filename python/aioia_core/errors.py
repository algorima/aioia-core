"""
Error handling infrastructure for AIoIA projects.

Provides standardized error codes and responses for FastAPI applications.
"""

from typing import Any, cast

from fastapi import HTTPException
from pydantic import BaseModel, Field

# ==============================================================================
# Error Codes
# ==============================================================================

# Authentication & Authorization errors
UNAUTHORIZED = "UNAUTHORIZED"
FORBIDDEN = "FORBIDDEN"
INVALID_TOKEN = "INVALID_TOKEN"
TOKEN_EXPIRED = "TOKEN_EXPIRED"
JWT_SECRET_NOT_CONFIGURED = "JWT_SECRET_NOT_CONFIGURED"

# Validation & Request errors
VALIDATION_ERROR = "VALIDATION_ERROR"
INVALID_JSON = "INVALID_JSON"
MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
INVALID_QUERY_PARAMS = "INVALID_QUERY_PARAMS"

# Resource Management errors
RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
RESOURCE_CREATION_FAILED = "RESOURCE_CREATION_FAILED"
RESOURCE_UPDATE_FAILED = "RESOURCE_UPDATE_FAILED"
RESOURCE_DELETE_FAILED = "RESOURCE_DELETE_FAILED"

# System & Server errors
INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
DATABASE_ERROR = "DATABASE_ERROR"
EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


# ==============================================================================
# Error Response Model
# ==============================================================================


class ErrorResponse(BaseModel):
    """
    Standardized error response model following RFC 9457 Problem Details for HTTP APIs.
    """

    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Human-readable error message")
    code: str = Field(
        ..., description="Machine-readable error code for client-side error handling"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "status": 401,
                    "detail": "Invalid authentication credentials",
                    "code": "INVALID_TOKEN",
                },
                {
                    "status": 404,
                    "detail": "Resource not found: item_123",
                    "code": "RESOURCE_NOT_FOUND",
                },
                {
                    "status": 422,
                    "detail": "Validation error in field 'email': Invalid email format",
                    "code": "VALIDATION_ERROR",
                },
            ]
        }


def extract_error_code_from_exception(exc: HTTPException) -> str:
    """HTTPException에서 에러 코드를 추출합니다."""
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return cast(dict[str, Any], exc.detail)["code"]

    # 상태 코드별 기본 에러 코드 매핑
    default_codes = {
        401: UNAUTHORIZED,
        403: FORBIDDEN,
        404: RESOURCE_NOT_FOUND,
        422: VALIDATION_ERROR,
        500: INTERNAL_SERVER_ERROR,
    }

    return default_codes.get(exc.status_code, INTERNAL_SERVER_ERROR)


def get_error_detail_from_exception(exc: HTTPException) -> str:
    """HTTPException에서 에러 상세 메시지를 추출합니다."""
    if isinstance(exc.detail, dict) and "detail" in exc.detail:
        return cast(dict[str, Any], exc.detail)["detail"]
    if isinstance(exc.detail, str):
        return exc.detail
    return str(exc.detail)
