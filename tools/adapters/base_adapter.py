from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAdapter(ABC):
    """
    Abstract base class for all language-specific or generic adapters.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def check_resource_policy(self, filepath: str, policy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check if a file violates a resource policy (e.g., dynamic_allocation).
        Returns a list of violation objects: {'line': int, 'message': str, 'severity': str}
        """
        pass

    @abstractmethod
    def check_side_effect_policy(self, filepath: str, policy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check if a file violates a side-effect policy (e.g., filesystem_write).
        Returns a list of violation objects.
        """
        pass
