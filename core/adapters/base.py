"""
Base adapter interface for external tools
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class Adapter(ABC):
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def extract(self, input_path: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def insert(self, input_path: str, data_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        pass
