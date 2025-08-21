"""
Base agent class for all specialized agents
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from loguru import logger
import asyncio

class BaseAgent(ABC):
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = logger.bind(agent=name)
    
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process input data and return result"""
        pass
    
    async def health_check(self) -> bool:
        """Check if agent is healthy and ready to process"""
        return True
    
    def log_info(self, message: str, **kwargs):
        self.logger.info(message, **kwargs)
    
    def log_error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        self.logger.warning(message, **kwargs)