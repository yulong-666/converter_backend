import time

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests (Access Logs).
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        process_time = time.perf_counter() - start_time
        process_time_ms = round(process_time * 1000, 2)
        
        client_host = request.client.host if request.client else "unknown"
        
        # Log with type="access" filter
        logger.bind(type="access").info(
            f"Client: {client_host} | "
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time_ms}ms"
        )
        
        return response
