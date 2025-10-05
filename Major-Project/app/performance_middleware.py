"""
Performance Monitoring Middleware
Tracks request latency and provides performance insights
"""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from app.performance_config import PerformanceConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("performance")

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor API performance"""
    
    def __init__(self, app, enable_logging: bool = True):
        super().__init__(app)
        self.enable_logging = enable_logging
        self.request_times = []
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        self.request_times.append(process_time)
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Performance-Optimized"] = "true"
        
        # Log slow requests
        if (self.enable_logging and 
            PerformanceConfig.LOG_SLOW_REQUESTS and 
            process_time > PerformanceConfig.SLOW_REQUEST_THRESHOLD):
            
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} "
                f"took {process_time:.2f}s"
            )
        
        # Log performance metrics for key endpoints
        if request.url.path in ["/analyze_emotion", "/record_answer", "/start_interview"]:
            logger.info(
                f"Performance: {request.method} {request.url.path} "
                f"completed in {process_time:.3f}s"
            )
        
        return response
    
    def get_average_response_time(self) -> float:
        """Get average response time across all requests"""
        if not self.request_times:
            return 0.0
        return sum(self.request_times) / len(self.request_times)
    
    def get_performance_stats(self) -> dict:
        """Get detailed performance statistics"""
        if not self.request_times:
            return {
                "total_requests": 0,
                "average_time": 0.0,
                "min_time": 0.0,
                "max_time": 0.0
            }
        
        return {
            "total_requests": len(self.request_times),
            "average_time": self.get_average_response_time(),
            "min_time": min(self.request_times),
            "max_time": max(self.request_times),
            "slow_requests": len([t for t in self.request_times 
                                if t > PerformanceConfig.SLOW_REQUEST_THRESHOLD])
        }