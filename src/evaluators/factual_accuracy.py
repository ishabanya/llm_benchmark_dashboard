"""Factual accuracy evaluator."""

import re
from typing import Any, Dict
from difflib import SequenceMatcher

from .base import Evaluator, TestCase, EvaluationResult
from models.base import ModelResponse


class FactualAccuracyEvaluator(Evaluator):
    """Evaluates factual accuracy of model responses."""
    
    def __init__(self):
        super().__init__("factual_accuracy")
    
    async def evaluate(
        self, 
        test_case: TestCase, 
        response: ModelResponse
    ) -> EvaluationResult:
        """Evaluate factual accuracy of the response."""
        try:
            expected = test_case.expected_answer
            actual = response.content.strip()
            
            if not expected:
                return self.create_result(
                    test_case, response, 0, 100,
                    {"error": "No expected answer provided"},
                    "No expected answer for comparison"
                )
            
            # Multiple evaluation methods
            scores = {}
            
            # 1. Exact match (case-insensitive)
            scores["exact_match"] = self._exact_match_score(expected, actual)
            
            # 2. Substring match
            scores["substring_match"] = self._substring_match_score(expected, actual)
            
            # 3. Token-based similarity
            scores["token_similarity"] = self._token_similarity_score(expected, actual)
            
            # 4. Number extraction and comparison
            scores["number_accuracy"] = self._number_accuracy_score(expected, actual)
            
            # 5. Key phrase detection
            scores["phrase_detection"] = self._phrase_detection_score(expected, actual)
            
            # Calculate weighted final score
            weights = {
                "exact_match": 0.3,
                "substring_match": 0.2,
                "token_similarity": 0.2,
                "number_accuracy": 0.15,
                "phrase_detection": 0.15
            }
            
            final_score = sum(scores[key] * weights[key] for key in scores)
            
            evaluation_details = {
                "expected_answer": expected,
                "actual_answer": actual,
                "component_scores": scores,
                "weights": weights,
                "final_score": final_score
            }
            
            return self.create_result(
                test_case, response, final_score, 100, evaluation_details
            )
            
        except Exception as e:
            return self.create_result(
                test_case, response, 0, 100,
                {"error": str(e)}, f"Evaluation error: {str(e)}"
            )
    
    def _exact_match_score(self, expected: str, actual: str) -> float:
        """Check for exact match (case-insensitive)."""
        return 100.0 if expected.lower().strip() == actual.lower().strip() else 0.0
    
    def _substring_match_score(self, expected: str, actual: str) -> float:
        """Check if expected answer is contained in actual response."""
        if expected.lower() in actual.lower():
            return 100.0
        return 0.0
    
    def _token_similarity_score(self, expected: str, actual: str) -> float:
        """Calculate token-based similarity."""
        expected_tokens = set(expected.lower().split())
        actual_tokens = set(actual.lower().split())
        
        if not expected_tokens:
            return 0.0
        
        intersection = expected_tokens.intersection(actual_tokens)
        union = expected_tokens.union(actual_tokens)
        
        if not union:
            return 0.0
        
        jaccard_score = len(intersection) / len(union)
        return jaccard_score * 100.0
    
    def _number_accuracy_score(self, expected: str, actual: str) -> float:
        """Extract and compare numbers in the responses."""
        expected_numbers = self._extract_numbers(expected)
        actual_numbers = self._extract_numbers(actual)
        
        if not expected_numbers:
            return 100.0  # No numbers to compare
        
        if not actual_numbers:
            return 0.0  # Expected numbers but found none
        
        # Check if all expected numbers are present
        matches = 0
        for exp_num in expected_numbers:
            if any(abs(exp_num - act_num) < 0.01 for act_num in actual_numbers):
                matches += 1
        
        return (matches / len(expected_numbers)) * 100.0
    
    def _extract_numbers(self, text: str) -> list[float]:
        """Extract numbers from text."""
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        numbers = []
        for match in matches:
            try:
                numbers.append(float(match))
            except ValueError:
                continue
        return numbers
    
    def _phrase_detection_score(self, expected: str, actual: str) -> float:
        """Detect key phrases from expected answer in actual response."""
        # Extract important phrases (2-4 words)
        expected_words = expected.lower().split()
        if len(expected_words) < 2:
            return self._substring_match_score(expected, actual)
        
        phrases = []
        for i in range(len(expected_words) - 1):
            phrase = " ".join(expected_words[i:i+2])
            phrases.append(phrase)
            if i < len(expected_words) - 2:
                longer_phrase = " ".join(expected_words[i:i+3])
                phrases.append(longer_phrase)
        
        if not phrases:
            return 0.0
        
        actual_lower = actual.lower()
        found_phrases = sum(1 for phrase in phrases if phrase in actual_lower)
        
        return (found_phrases / len(phrases)) * 100.0
    
    def get_evaluation_criteria(self) -> Dict[str, Any]:
        """Get evaluation criteria for factual accuracy."""
        return {
            "name": "Factual Accuracy",
            "description": "Evaluates how accurately the model provides factual information",
            "scoring_components": {
                "exact_match": "Perfect match with expected answer (30%)",
                "substring_match": "Expected answer contained in response (20%)",
                "token_similarity": "Similarity based on word overlap (20%)",
                "number_accuracy": "Accuracy of numerical values (15%)",
                "phrase_detection": "Detection of key phrases (15%)"
            },
            "passing_threshold": 70.0,
            "max_score": 100.0
        }