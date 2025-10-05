# Performance Configuration
# This file contains all performance-related settings for the AI Interview Coach

from typing import Dict, Any

class PerformanceConfig:
    """Configuration class for performance optimizations"""
    
    # Cache settings
    EMOTION_CACHE_SIZE = 1000
    EMOTION_CACHE_TTL = 30  # seconds
    QUESTION_CACHE_SIZE = 100
    QUESTION_CACHE_TTL = 300  # seconds
    
    # Async processing settings
    MAX_BATCH_SIZE = 5
    THREAD_POOL_SIZE = 4
    
    # Model optimization
    PRELOAD_MODELS_ON_STARTUP = True
    MODEL_CACHE_ENABLED = True
    
    # JSON serialization
    USE_ORJSON = True
    
    # Image processing
    MAX_IMAGE_SIZE = (640, 480)  # Resize large images for faster processing
    IMAGE_QUALITY = 85  # JPEG quality for base64 images
    
    # Performance monitoring
    ENABLE_PERFORMANCE_METRICS = True
    LOG_SLOW_REQUESTS = True
    SLOW_REQUEST_THRESHOLD = 1.0  # seconds
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Get cache configuration"""
        return {
            'emotion_cache': {
                'maxsize': cls.EMOTION_CACHE_SIZE,
                'ttl': cls.EMOTION_CACHE_TTL
            },
            'question_cache': {
                'maxsize': cls.QUESTION_CACHE_SIZE,
                'ttl': cls.QUESTION_CACHE_TTL
            }
        }
    
    @classmethod
    def get_async_config(cls) -> Dict[str, Any]:
        """Get async processing configuration"""
        return {
            'max_batch_size': cls.MAX_BATCH_SIZE,
            'thread_pool_size': cls.THREAD_POOL_SIZE
        }
    
    @classmethod
    def get_optimization_summary(cls) -> Dict[str, bool]:
        """Get summary of enabled optimizations"""
        return {
            'caching_enabled': True,
            'async_processing': True,
            'orjson_serialization': cls.USE_ORJSON,
            'model_preloading': cls.PRELOAD_MODELS_ON_STARTUP,
            'batch_processing': True,
            'performance_monitoring': cls.ENABLE_PERFORMANCE_METRICS
        }