from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
import traceback
from app.utils.correlation import get_correlation_id

logger = logging.getLogger(__name__)


class BaseAPIException(HTTPException):
    """Base exception for API errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__


class ValidationError(BaseAPIException):
    """Validation error."""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )
        self.field = field


class NotFoundError(BaseAPIException):
    """Resource not found error."""
    
    def __init__(self, resource: str, identifier: Any = None):
        detail = f"{resource} not found"
        if identifier:
            detail += f" with identifier: {identifier}"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND"
        )


class ConflictError(BaseAPIException):
    """Resource conflict error."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT"
        )


class InsufficientSeatsError(BaseAPIException):
    """Insufficient seats available."""
    
    def __init__(self, available: int, requested: int):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Insufficient seats. Available: {available}, Requested: {requested}",
            error_code="INSUFFICIENT_SEATS"
        )


class UnauthorizedError(BaseAPIException):
    """Unauthorized access error."""
    
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="UNAUTHORIZED"
        )


class ForbiddenError(BaseAPIException):
    """Forbidden access error."""
    
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="FORBIDDEN"
        )


def create_error_response(
    status_code: int,
    message: str,
    error_code: str,
    correlation_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create standardized error response."""
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": "2024-01-01T00:00:00Z",  # Use actual timestamp
        }
    }
    
    if correlation_id:
        response["correlation_id"] = correlation_id
    
    if details:
        response["error"]["details"] = details
    
    return response


async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    """Handle BaseAPIException."""
    correlation_id = get_correlation_id()
    
    logger.warning(
        f"API Exception: {exc.error_code} - {exc.detail}",
        extra={
            "correlation_id": correlation_id,
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=exc.detail,
            error_code=exc.error_code,
            correlation_id=correlation_id,
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    correlation_id = get_correlation_id()
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(
        f"Validation error: {len(errors)} validation errors",
        extra={
            "correlation_id": correlation_id,
            "errors": errors,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation failed",
            error_code="VALIDATION_ERROR",
            correlation_id=correlation_id,
            details={"errors": errors}
        )
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy errors."""
    correlation_id = get_correlation_id()
    
    if isinstance(exc, IntegrityError):
        logger.warning(
            f"Database integrity error: {str(exc)}",
            extra={"correlation_id": correlation_id}
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=create_error_response(
                status_code=status.HTTP_409_CONFLICT,
                message="Data integrity constraint violation",
                error_code="INTEGRITY_ERROR",
                correlation_id=correlation_id,
            )
        )
    
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "correlation_id": correlation_id,
            "traceback": traceback.format_exc(),
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            error_code="DATABASE_ERROR",
            correlation_id=correlation_id,
        )
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    correlation_id = get_correlation_id()
    
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "correlation_id": correlation_id,
            "traceback": traceback.format_exc(),
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            correlation_id=correlation_id,
        )
    )