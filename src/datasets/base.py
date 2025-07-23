"""Base classes for test datasets."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from evaluators.base import TestCase


class Dataset(ABC):
    """Abstract base class for test datasets."""
    
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
    
    @abstractmethod
    def get_test_cases(self) -> List[TestCase]:
        """Get all test cases in this dataset."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get dataset metadata."""
        pass


class TestCaseLoader:
    """Utility class for loading and managing test cases."""
    
    @staticmethod
    def create_test_case(
        test_id: str,
        category: str,
        subcategory: str,
        difficulty: str,
        prompt: str,
        expected_answer: str = None,
        system_prompt: str = None,
        evaluation_criteria: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> TestCase:
        """Create a test case with proper validation."""
        return TestCase(
            id=test_id,
            category=category,
            subcategory=subcategory,
            difficulty=difficulty,
            prompt=prompt,
            system_prompt=system_prompt,
            expected_answer=expected_answer,
            evaluation_criteria=evaluation_criteria or {},
            metadata=metadata or {}
        )