"""JSON report generator."""

import json
import os
from typing import Dict, Any, Optional

from .base import ReportGenerator


class JSONReporter(ReportGenerator):
    """Generates JSON reports from evaluation data."""
    
    def generate_report(
        self, 
        evaluation_data: Dict[str, Any], 
        filename: Optional[str] = None
    ) -> str:
        """Generate JSON report."""
        if not filename:
            filename = self.get_default_filename("json")
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Ensure the data is JSON serializable
        clean_data = self._clean_for_json(evaluation_data)
        
        with open(filepath, 'w') as f:
            json.dump(clean_data, f, indent=2, default=str)
        
        return filepath
    
    def _clean_for_json(self, data: Any) -> Any:
        """Clean data to make it JSON serializable."""
        if isinstance(data, dict):
            return {k: self._clean_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._clean_for_json(item) for item in data]
        elif hasattr(data, 'isoformat'):  # datetime objects
            return data.isoformat()
        else:
            return data