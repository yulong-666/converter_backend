import time
from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to capture HTTP request/response details and log them to the 'access' log.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
        except Exception as e:
            # Calculate time even if failed
            process_time = time.perf_counter() - start_time
            process_time_ms = round(process_time * 1000, 2)
            
            client_ip = request.client.host if request.client else "unknown"
            
            # Log the error to access log as well (or just rely on error log)
            # Binding name="access" ensures it goes to logs/access.log
            logger.bind(name="access").error(
                f"Client: {client_ip} | Method: {request.method} | Path: {request.url.path} | "
                f"Status: 500 | Time: {process_time_ms}ms | Error: {str(e)}"
            )
            raise e

        process_time = time.perf_counter() - start_time
        process_time_ms = round(process_time * 1000, 2)
        
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log to access log
        logger.bind(name="access").info(
            f"Client: {client_ip} | "
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time_ms}ms | "
            f"User-Agent: {user_agent}"
        )
        
        return response
