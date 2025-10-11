"""SQL Agent interface definition"""

from abc import ABC, abstractmethod
from typing import Optional


class SQLAgent(ABC):
    """Base interface for SQL Agent
    
    Users need to inherit this interface and implement the optimize method to create custom SQL Agents
    """
    
    @abstractmethod
    def optimize(self, sql_query: str) -> str:
        """Optimize SQL query
        
        Args:
            sql_query: SQL query statement that needs optimization
            
        Returns:
            str: Optimization suggestions, including specific optimization solutions and reasoning
        """
        pass
    
    def get_name(self) -> str:
        """Get Agent name for report display
        
        Returns:
            str: Agent name, defaults to class name
        """
        return self.__class__.__name__
    
    def get_description(self) -> Optional[str]:
        """Get Agent description information
        
        Returns:
            str: Agent description, defaults to None
        """
        return None
