"""CSV report generator for detailed analysis."""

import csv
import os
from typing import Dict, Any, Optional, List

from .base import ReportGenerator


class CSVReporter(ReportGenerator):
    """Generates CSV reports from evaluation data."""
    
    def generate_report(
        self, 
        evaluation_data: Dict[str, Any], 
        filename: Optional[str] = None
    ) -> str:
        """Generate CSV report with detailed results."""
        if not filename:
            filename = self.get_default_filename("csv")
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Extract results data
        results = evaluation_data.get("results", [])
        
        if not results:
            # Create empty CSV with headers
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["No results available"])
            return filepath
        
        # Define CSV headers
        headers = [
            "test_case_id", "provider", "model", "category", "subcategory", 
            "difficulty", "score", "max_score", "passed", "prompt_tokens",
            "completion_tokens", "total_tokens", "cost_usd", "latency_ms",
            "timestamp", "error"
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for result in results:
                response = result.get("response", {})
                
                row = [
                    result.get("test_case_id", ""),
                    result.get("provider", ""),
                    response.get("model", ""),
                    result.get("category", ""),
                    result.get("subcategory", ""),
                    result.get("difficulty", ""),
                    result.get("score", 0),
                    result.get("max_score", 100),
                    result.get("passed", False),
                    response.get("prompt_tokens", 0),
                    response.get("completion_tokens", 0),
                    response.get("total_tokens", 0),
                    response.get("cost_usd", 0.0),
                    response.get("latency_ms", 0.0),
                    result.get("timestamp", ""),
                    result.get("error", "")
                ]
                
                writer.writerow(row)
        
        # Also generate summary CSV
        summary_filepath = self._generate_summary_csv(evaluation_data, filename)
        
        return filepath
    
    def _generate_summary_csv(
        self, 
        evaluation_data: Dict[str, Any], 
        main_filename: str
    ) -> str:
        """Generate a summary CSV with provider metrics."""
        summary_filename = main_filename.replace('.csv', '_summary.csv')
        summary_filepath = os.path.join(self.output_dir, summary_filename)
        
        metrics = evaluation_data.get("metrics", {})
        provider_metrics = metrics.get("provider_metrics", {})
        
        if not provider_metrics:
            return summary_filepath
        
        headers = [
            "provider", "total_evaluations", "average_score", "median_score",
            "pass_rate", "total_cost_usd", "average_latency_ms", "reliability_score"
        ]
        
        with open(summary_filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for provider, metrics_data in provider_metrics.items():
                row = [
                    provider,
                    metrics_data.get("total_evaluations", 0),
                    metrics_data.get("average_score", 0),
                    metrics_data.get("median_score", 0),
                    metrics_data.get("pass_rate", 0),
                    metrics_data.get("total_cost_usd", 0.0),
                    metrics_data.get("average_latency_ms", 0.0),
                    metrics_data.get("reliability_score", 0.0)
                ]
                writer.writerow(row)
        
        return summary_filepath