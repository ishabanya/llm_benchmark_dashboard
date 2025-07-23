"""Dataset loader utility."""

from typing import List, Dict, Any, Type

from .base import Dataset
from .factual_accuracy_data import FactualAccuracyDataset
from .reasoning_logic_data import ReasoningLogicDataset
from .code_generation_data import CodeGenerationDataset
from .safety_bias_data import SafetyBiasDataset
from .instruction_following_data import InstructionFollowingDataset
from evaluators.base import TestCase


class DatasetLoader:
    """Loads and manages all test datasets."""
    
    _datasets: Dict[str, Type[Dataset]] = {
        "factual_accuracy": FactualAccuracyDataset,
        "reasoning_logic": ReasoningLogicDataset,
        "code_generation": CodeGenerationDataset,
        "safety_bias": SafetyBiasDataset,
        "instruction_following": InstructionFollowingDataset,
    }
    
    @classmethod
    def get_all_datasets(cls) -> List[Dataset]:
        """Get all available datasets."""
        return [dataset_class() for dataset_class in cls._datasets.values()]
    
    @classmethod
    def get_dataset(cls, name: str) -> Dataset:
        """Get a specific dataset by name."""
        if name not in cls._datasets:
            available = ", ".join(cls._datasets.keys())
            raise ValueError(f"Unknown dataset '{name}'. Available: {available}")
        
        return cls._datasets[name]()
    
    @classmethod
    def get_all_test_cases(cls) -> List[TestCase]:
        """Get all test cases from all datasets."""
        all_cases = []
        for dataset in cls.get_all_datasets():
            all_cases.extend(dataset.get_test_cases())
        return all_cases
    
    @classmethod
    def get_test_cases_by_category(cls, category: str) -> List[TestCase]:
        """Get test cases for a specific category."""
        try:
            dataset = cls.get_dataset(category)
            return dataset.get_test_cases()
        except ValueError:
            return []
    
    @classmethod
    def get_test_cases_by_difficulty(cls, difficulty: str) -> List[TestCase]:
        """Get test cases filtered by difficulty."""
        all_cases = cls.get_all_test_cases()
        return [case for case in all_cases if case.difficulty == difficulty]
    
    @classmethod
    def get_dataset_summary(cls) -> Dict[str, Any]:
        """Get summary of all datasets."""
        summary = {
            "total_datasets": len(cls._datasets),
            "datasets": {},
            "total_test_cases": 0,
            "difficulty_distribution": {"easy": 0, "medium": 0, "hard": 0},
            "category_distribution": {}
        }
        
        for dataset in cls.get_all_datasets():
            metadata = dataset.get_metadata()
            test_cases = dataset.get_test_cases()
            
            summary["datasets"][dataset.name] = {
                "description": metadata.get("description", ""),
                "total_cases": len(test_cases),
                "subcategories": metadata.get("subcategories", [])
            }
            
            summary["total_test_cases"] += len(test_cases)
            
            # Count by difficulty
            for case in test_cases:
                if case.difficulty in summary["difficulty_distribution"]:
                    summary["difficulty_distribution"][case.difficulty] += 1
            
            # Count by category
            if dataset.category not in summary["category_distribution"]:
                summary["category_distribution"][dataset.category] = 0
            summary["category_distribution"][dataset.category] += len(test_cases)
        
        return summary
    
    @classmethod
    def get_available_categories(cls) -> List[str]:
        """Get list of available dataset categories."""
        return list(cls._datasets.keys())