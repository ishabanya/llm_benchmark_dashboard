"""Reasoning and logic evaluator."""

import re
import ast
from typing import Any, Dict

from .base import Evaluator, TestCase, EvaluationResult
from models.base import ModelResponse


class ReasoningLogicEvaluator(Evaluator):
    """Evaluates reasoning and logical thinking capabilities."""
    
    def __init__(self):
        super().__init__("reasoning_logic")
    
    async def evaluate(
        self, 
        test_case: TestCase, 
        response: ModelResponse
    ) -> EvaluationResult:
        """Evaluate reasoning and logic in the response."""
        try:
            expected = test_case.expected_answer
            actual = response.content.strip()
            
            scores = {}
            
            # 1. Final answer correctness
            scores["answer_correctness"] = self._check_final_answer(expected, actual)
            
            # 2. Reasoning process evaluation
            scores["reasoning_process"] = self._evaluate_reasoning_process(actual)
            
            # 3. Logical structure
            scores["logical_structure"] = self._evaluate_logical_structure(actual)
            
            # 4. Step-by-step approach
            scores["step_by_step"] = self._evaluate_step_by_step(actual)
            
            # 5. Mathematical accuracy (if applicable)
            scores["mathematical_accuracy"] = self._evaluate_mathematical_accuracy(actual, expected)
            
            # Calculate weighted final score
            weights = {
                "answer_correctness": 0.4,
                "reasoning_process": 0.25,
                "logical_structure": 0.15,
                "step_by_step": 0.1,
                "mathematical_accuracy": 0.1
            }
            
            final_score = sum(scores[key] * weights[key] for key in scores)
            
            evaluation_details = {
                "expected_answer": expected,
                "actual_answer": actual,
                "component_scores": scores,
                "weights": weights,
                "final_score": final_score,
                "reasoning_indicators": self._find_reasoning_indicators(actual)
            }
            
            return self.create_result(
                test_case, response, final_score, 100, evaluation_details
            )
            
        except Exception as e:
            return self.create_result(
                test_case, response, 0, 100,
                {"error": str(e)}, f"Evaluation error: {str(e)}"
            )
    
    def _check_final_answer(self, expected: str, actual: str) -> float:
        """Check if the final answer is correct."""
        if not expected:
            return 100.0
        
        # Extract the final answer from the response
        final_answer = self._extract_final_answer(actual)
        
        # Try multiple comparison methods
        if expected.lower().strip() == final_answer.lower().strip():
            return 100.0
        
        # Check if expected answer appears anywhere in the response
        if expected.lower() in actual.lower():
            return 80.0
        
        # Check numerical answers
        expected_nums = self._extract_numbers(expected)
        actual_nums = self._extract_numbers(final_answer)
        
        if expected_nums and actual_nums:
            for exp_num in expected_nums:
                if any(abs(exp_num - act_num) < 0.01 for act_num in actual_nums):
                    return 100.0
        
        return 0.0
    
    def _extract_final_answer(self, text: str) -> str:
        """Extract the final answer from the response."""
        # Look for common patterns
        patterns = [
            r"(?:answer|result|solution)(?:\s*is)?\s*:?\s*(.+?)(?:\n|$)",
            r"(?:therefore|thus|so|hence)[:,]?\s*(.+?)(?:\n|$)",
            r"final answer(?:\s*is)?\s*:?\s*(.+?)(?:\n|$)",
            r"the answer is\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern found, return the last line
        lines = text.strip().split('\n')
        return lines[-1].strip() if lines else text
    
    def _evaluate_reasoning_process(self, text: str) -> float:
        """Evaluate the quality of the reasoning process."""
        score = 0.0
        max_score = 100.0
        
        # Check for reasoning indicators
        reasoning_words = [
            "because", "since", "therefore", "thus", "hence", "so",
            "given that", "assuming", "if", "then", "consider",
            "let's think", "first", "second", "next", "finally"
        ]
        
        found_reasoning = sum(1 for word in reasoning_words if word in text.lower())
        score += min(40, found_reasoning * 5)  # Max 40 points for reasoning words
        
        # Check for logical connectors
        connectors = ["and", "but", "however", "moreover", "furthermore", "additionally"]
        found_connectors = sum(1 for conn in connectors if conn in text.lower())
        score += min(20, found_connectors * 3)  # Max 20 points for connectors
        
        # Check for explanation length (reasonable explanation)
        if len(text.split()) > 20:
            score += 20
        elif len(text.split()) > 10:
            score += 10
        
        # Check for question analysis
        if any(word in text.lower() for word in ["analyze", "break down", "examine"]):
            score += 20
        
        return min(max_score, score)
    
    def _evaluate_logical_structure(self, text: str) -> float:
        """Evaluate the logical structure of the response."""
        score = 0.0
        
        # Check for structured thinking
        structure_indicators = [
            r"\d+\.", r"step \d+", r"first", r"second", r"third",
            r"a\)", r"b\)", r"c\)", r"-", r"•"
        ]
        
        structure_count = 0
        for pattern in structure_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                structure_count += 1
        
        if structure_count >= 3:
            score += 50
        elif structure_count >= 2:
            score += 30
        elif structure_count >= 1:
            score += 15
        
        # Check for premise-conclusion structure
        if any(word in text.lower() for word in ["premise", "assumption", "given", "conclusion"]):
            score += 25
        
        # Check for conditional reasoning
        if "if" in text.lower() and "then" in text.lower():
            score += 25
        
        return min(100.0, score)
    
    def _evaluate_step_by_step(self, text: str) -> float:
        """Evaluate step-by-step problem solving."""
        score = 0.0
        
        # Count steps
        step_patterns = [
            r"step \d+", r"\d+\.", r"first", r"second", r"third", r"fourth", r"fifth",
            r"next", r"then", r"after that", r"finally"
        ]
        
        steps_found = 0
        for pattern in step_patterns:
            steps_found += len(re.findall(pattern, text, re.IGNORECASE))
        
        if steps_found >= 4:
            score = 100.0
        elif steps_found >= 3:
            score = 80.0
        elif steps_found >= 2:
            score = 60.0
        elif steps_found >= 1:
            score = 40.0
        
        return score
    
    def _evaluate_mathematical_accuracy(self, actual: str, expected: str) -> float:
        """Evaluate mathematical calculations if present."""
        # Extract mathematical expressions
        math_pattern = r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)'
        matches = re.findall(math_pattern, actual)
        
        if not matches:
            return 100.0  # No math to evaluate
        
        correct_calculations = 0
        total_calculations = len(matches)
        
        for match in matches:
            num1, operator, num2, result = match
            try:
                num1, num2, result = float(num1), float(num2), float(result)
                
                if operator == '+':
                    expected_result = num1 + num2
                elif operator == '-':
                    expected_result = num1 - num2
                elif operator == '*':
                    expected_result = num1 * num2
                elif operator == '/':
                    expected_result = num1 / num2 if num2 != 0 else float('inf')
                else:
                    continue
                
                if abs(result - expected_result) < 0.01:
                    correct_calculations += 1
                    
            except (ValueError, ZeroDivisionError):
                continue
        
        return (correct_calculations / total_calculations) * 100.0 if total_calculations > 0 else 100.0
    
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
    
    def _find_reasoning_indicators(self, text: str) -> Dict[str, bool]:
        """Find various reasoning indicators in the text."""
        return {
            "has_premises": any(word in text.lower() for word in ["given", "assume", "premise"]),
            "has_conclusion": any(word in text.lower() for word in ["therefore", "thus", "conclusion"]),
            "has_conditional": "if" in text.lower() and "then" in text.lower(),
            "has_explanation": any(word in text.lower() for word in ["because", "since", "reason"]),
            "has_steps": any(word in text.lower() for word in ["step", "first", "second", "next"]),
            "has_analysis": any(word in text.lower() for word in ["analyze", "examine", "consider"])
        }
    
    def get_evaluation_criteria(self) -> Dict[str, Any]:
        """Get evaluation criteria for reasoning and logic."""
        return {
            "name": "Reasoning & Logic",
            "description": "Evaluates logical thinking and reasoning capabilities",
            "scoring_components": {
                "answer_correctness": "Correctness of final answer (40%)",
                "reasoning_process": "Quality of reasoning process (25%)",
                "logical_structure": "Logical structure and organization (15%)",
                "step_by_step": "Step-by-step problem solving (10%)",
                "mathematical_accuracy": "Accuracy of calculations (10%)"
            },
            "passing_threshold": 70.0,
            "max_score": 100.0
        }