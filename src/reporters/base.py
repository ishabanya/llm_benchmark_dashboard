"""Base report generator interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os


class ReportGenerator(ABC):
    """Abstract base class for report generators."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    @abstractmethod
    def generate_report(
        self, 
        evaluation_data: Dict[str, Any], 
        filename: Optional[str] = None
    ) -> str:
        """Generate a report from evaluation data.
        
        Args:
            evaluation_data: Complete evaluation results
            filename: Optional custom filename
            
        Returns:
            Path to generated report file
        """
        pass
    
    def get_default_filename(self, extension: str) -> str:
        """Generate default filename with timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"llm_benchmark_report_{timestamp}.{extension}"