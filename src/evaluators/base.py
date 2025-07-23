"""Base classes for evaluators."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime

from models.base import ModelResponse


@dataclass
class TestCase:
    """A single test case for evaluation."""
    id: str
    category: str
    subcategory: str
    difficulty: str  # easy, medium, hard
    prompt: str
    system_prompt: Optional[str] = None
    expected_answer: Optional[str] = None
    evaluation_criteria: Dict[str, Any] = None
    metadata: Dict[str, Any] = None


@dataclass
class EvaluationResult:
    """Result of evaluating a model response."""
    test_case_id: str
    model: str
    provider: str
    category: str
    subcategory: str
    difficulty: str
    score: float  # 0-100 normalized score
    max_score: float
    passed: bool
    response: ModelResponse
    evaluation_details: Dict[str, Any]
    timestamp: datetime
    error: Optional[str] = None


class Evaluator(ABC):
    """Abstract base class for evaluators."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def evaluate(
        self, 
        test_case: TestCase, 
        response: ModelResponse
    ) -> EvaluationResult:
        """Evaluate a model response against a test case."""
        pass
    
    @abstractmethod
    def get_evaluation_criteria(self) -> Dict[str, Any]:
        """Get the evaluation criteria for this evaluator."""
        pass
    
    def normalize_score(self, raw_score: float, max_score: float) -> float:
        """Normalize score to 0-100 scale."""
        if max_score == 0:
            return 0.0
        return min(100.0, max(0.0, (raw_score / max_score) * 100.0))
    
    def create_result(
        self,
        test_case: TestCase,
        response: ModelResponse,
        score: float,
        max_score: float,
        evaluation_details: Dict[str, Any],
        error: Optional[str] = None
    ) -> EvaluationResult:
        """Create an evaluation result."""
        normalized_score = self.normalize_score(score, max_score)
        
        return EvaluationResult(
            test_case_id=test_case.id,
            model=response.model,
            provider=response.provider,
            category=test_case.category,
            subcategory=test_case.subcategory,
            difficulty=test_case.difficulty,
            score=normalized_score,
            max_score=max_score,
            passed=normalized_score >= 70.0,  # 70% threshold for passing
            response=response,
            evaluation_details=evaluation_details,
            timestamp=datetime.now(),
            error=error
        )