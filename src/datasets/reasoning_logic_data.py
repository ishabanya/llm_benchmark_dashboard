"""Reasoning and logic test dataset."""

from typing import List, Dict, Any

from .base import Dataset, TestCaseLoader
from evaluators.base import TestCase


class ReasoningLogicDataset(Dataset):
    """Dataset for reasoning and logic evaluation."""
    
    def __init__(self):
        super().__init__("reasoning_logic", "reasoning_logic")
    
    def get_test_cases(self) -> List[TestCase]:
        """Get all reasoning and logic test cases."""
        test_cases = []
        
        # Easy reasoning questions
        easy_cases = [
            {
                "id": "reason_easy_001",
                "subcategory": "basic_logic",
                "difficulty": "easy",
                "prompt": "If all roses are flowers and all flowers need water, do roses need water?",
                "expected_answer": "Yes",
                "metadata": {"type": "syllogism", "topic": "logical_deduction"}
            },
            {
                "id": "reason_easy_002",
                "subcategory": "basic_math",
                "difficulty": "easy",
                "prompt": "If a train travels 60 miles in 1 hour, how far will it travel in 3 hours at the same speed?",
                "expected_answer": "180 miles",
                "metadata": {"type": "proportion", "topic": "distance_calculation"}
            },
            {
                "id": "reason_easy_003",
                "subcategory": "pattern_recognition",
                "difficulty": "easy", 
                "prompt": "What comes next in this sequence: 2, 4, 6, 8, ?",
                "expected_answer": "10",
                "metadata": {"type": "arithmetic_sequence", "topic": "number_patterns"}
            },
            {
                "id": "reason_easy_004",
                "subcategory": "basic_logic",
                "difficulty": "easy",
                "prompt": "If it's raining, then the ground is wet. The ground is wet. Can we conclude it's raining?",
                "expected_answer": "No",
                "metadata": {"type": "logical_fallacy", "topic": "affirming_consequent"}
            },
            {
                "id": "reason_easy_005",
                "subcategory": "basic_math",
                "difficulty": "easy",
                "prompt": "A rectangle has a length of 8 units and width of 5 units. What is its area?",
                "expected_answer": "40 square units",
                "metadata": {"type": "geometry", "topic": "area_calculation"}
            },
            {
                "id": "reason_easy_006",
                "subcategory": "word_problems",
                "difficulty": "easy",
                "prompt": "Sarah has 15 apples. She gives 7 apples to her friend. How many apples does Sarah have left?",
                "expected_answer": "8 apples",
                "metadata": {"type": "subtraction", "topic": "basic_arithmetic"}
            },
            {
                "id": "reason_easy_007",
                "subcategory": "pattern_recognition",
                "difficulty": "easy",
                "prompt": "Complete the pattern: A, C, E, G, ?",
                "expected_answer": "I",
                "metadata": {"type": "letter_sequence", "topic": "alphabetical_patterns"}
            },
            {
                "id": "reason_easy_008",
                "subcategory": "basic_logic",
                "difficulty": "easy",
                "prompt": "If some cats are black and some black things are cars, are some cats cars?",
                "expected_answer": "No",
                "metadata": {"type": "logical_reasoning", "topic": "invalid_syllogism"}
            }
        ]
        
        # Medium reasoning questions
        medium_cases = [
            {
                "id": "reason_medium_001",
                "subcategory": "mathematical_reasoning",
                "difficulty": "medium",
                "prompt": "A bag contains 3 red balls and 5 blue balls. If you randomly pick 2 balls without replacement, what's the probability both are red?",
                "expected_answer": "3/28 or approximately 0.107",
                "metadata": {"type": "probability", "topic": "combinatorics"}
            },
            {
                "id": "reason_medium_002",
                "subcategory": "logical_puzzles", 
                "difficulty": "medium",
                "prompt": "In a certain code, 'HELLO' is written as 'IFMMP'. How would 'WORLD' be written in the same code?",
                "expected_answer": "XPSME",
                "metadata": {"type": "cipher", "topic": "pattern_decoding"}
            },
            {
                "id": "reason_medium_003",
                "subcategory": "analytical_reasoning",
                "difficulty": "medium",
                "prompt": "Five friends sit in a row. Alice sits next to Bob. Carol sits at one end. David sits between Bob and Emily. Who sits at the other end?",
                "expected_answer": "Alice",
                "metadata": {"type": "seating_arrangement", "topic": "logical_deduction"}
            },
            {
                "id": "reason_medium_004",
                "subcategory": "mathematical_reasoning",
                "difficulty": "medium",
                "prompt": "If x + y = 10 and x - y = 4, what are the values of x and y?",
                "expected_answer": "x = 7, y = 3",
                "metadata": {"type": "system_equations", "topic": "algebra"}
            },
            {
                "id": "reason_medium_005",
                "subcategory": "logical_puzzles",
                "difficulty": "medium",
                "prompt": "A clock shows 3:15. What is the angle between the hour and minute hands?",
                "expected_answer": "7.5 degrees",
                "metadata": {"type": "clock_problem", "topic": "angle_calculation"}
            },
            {
                "id": "reason_medium_006",
                "subcategory": "word_problems",
                "difficulty": "medium",
                "prompt": "A car travels from city A to city B at 60 mph and returns at 40 mph. If the total trip takes 5 hours, what is the distance between the cities?",
                "expected_answer": "120 miles",
                "metadata": {"type": "distance_time", "topic": "average_speed"}
            },
            {
                "id": "reason_medium_007",
                "subcategory": "analytical_reasoning",
                "difficulty": "medium",
                "prompt": "Every politician is dishonest. John is honest. Therefore, John is not a politician. Is this reasoning valid?",
                "expected_answer": "Yes",
                "metadata": {"type": "modus_tollens", "topic": "logical_validity"}
            },
            {
                "id": "reason_medium_008",
                "subcategory": "mathematical_reasoning",
                "difficulty": "medium",
                "prompt": "What is the next number in the Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13, ?",
                "expected_answer": "21",
                "metadata": {"type": "fibonacci", "topic": "mathematical_sequences"}
            },
            {
                "id": "reason_medium_009",
                "subcategory": "logical_puzzles",
                "difficulty": "medium",
                "prompt": "Three boxes contain balls. Box A has 2 red balls, Box B has 1 red and 1 blue ball, Box C has 2 blue balls. You randomly pick a box and draw a red ball. What's the probability you picked Box A?",
                "expected_answer": "2/3 or approximately 0.667",
                "metadata": {"type": "bayes_theorem", "topic": "conditional_probability"}
            }
        ]
        
        # Hard reasoning questions
        hard_cases = [
            {
                "id": "reason_hard_001",
                "subcategory": "complex_logic",
                "difficulty": "hard",
                "prompt": "In a village, the barber shaves only those who do not shave themselves. Who shaves the barber?",
                "expected_answer": "This is a paradox with no logical solution (Russell's Paradox variant)",
                "metadata": {"type": "paradox", "topic": "self_reference"}
            },
            {
                "id": "reason_hard_002",
                "subcategory": "advanced_math",
                "difficulty": "hard",
                "prompt": "Find the sum of the infinite geometric series: 1 + 1/2 + 1/4 + 1/8 + ...",
                "expected_answer": "2",
                "metadata": {"type": "infinite_series", "topic": "geometric_series"}
            },
            {
                "id": "reason_hard_003",
                "subcategory": "complex_puzzles",
                "difficulty": "hard",
                "prompt": "You have 12 balls, one of which is either heavier or lighter than the others. Using a balance scale only 3 times, how can you identify the odd ball and determine if it's heavier or lighter?",
                "expected_answer": "Divide into groups of 4-4-4, then use systematic weighing to isolate and identify the odd ball",
                "metadata": {"type": "weighing_puzzle", "topic": "optimization"}
            },
            {
                "id": "reason_hard_004",
                "subcategory": "advanced_math",
                "difficulty": "hard",
                "prompt": "If f(x) = x² + 2x + 1, what is the derivative f'(x)?",
                "expected_answer": "2x + 2",
                "metadata": {"type": "calculus", "topic": "derivatives"}
            },
            {
                "id": "reason_hard_005",
                "subcategory": "complex_logic",
                "difficulty": "hard",
                "prompt": "In a game show, there are 3 doors. Behind one is a car, behind the other two are goats. You pick door 1. The host opens door 3, revealing a goat. Should you switch to door 2?",
                "expected_answer": "Yes, switching gives you a 2/3 probability of winning",
                "metadata": {"type": "monty_hall", "topic": "probability_paradox"}
            },
            {
                "id": "reason_hard_006",
                "subcategory": "advanced_math",
                "difficulty": "hard",
                "prompt": "Prove that the square root of 2 is irrational.",
                "expected_answer": "Use proof by contradiction: assume √2 = p/q in lowest terms, then show p and q must both be even, contradicting lowest terms assumption",
                "metadata": {"type": "mathematical_proof", "topic": "number_theory"}
            },
            {
                "id": "reason_hard_007",
                "subcategory": "complex_puzzles",
                "difficulty": "hard",
                "prompt": "Four people need to cross a bridge at night with one flashlight. The bridge holds only 2 people at a time. Crossing times are 1, 2, 5, and 10 minutes. What's the minimum time for all to cross?",
                "expected_answer": "17 minutes",
                "metadata": {"type": "optimization_puzzle", "topic": "strategic_thinking"}
            },
            {
                "id": "reason_hard_008",
                "subcategory": "complex_logic",
                "difficulty": "hard",
                "prompt": "If every statement I make is false, and I say 'This statement is false', what can you conclude?",
                "expected_answer": "This creates a logical paradox (liar paradox) that cannot be resolved within classical logic",
                "metadata": {"type": "self_reference_paradox", "topic": "metalogic"}
            }
        ]
        
        # Create test cases
        all_cases = easy_cases + medium_cases + hard_cases
        
        for case_data in all_cases:
            test_case = TestCaseLoader.create_test_case(
                test_id=case_data["id"],
                category=self.category,
                subcategory=case_data["subcategory"],
                difficulty=case_data["difficulty"],
                prompt=case_data["prompt"],
                expected_answer=case_data["expected_answer"],
                metadata=case_data["metadata"]
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get dataset metadata."""
        return {
            "name": self.name,
            "category": self.category,
            "description": "Tests logical reasoning, mathematical thinking, and problem-solving abilities",
            "total_cases": 25,
            "difficulty_distribution": {
                "easy": 8,
                "medium": 9, 
                "hard": 8
            },
            "subcategories": [
                "basic_logic", "basic_math", "pattern_recognition", "word_problems",
                "mathematical_reasoning", "logical_puzzles", "analytical_reasoning",
                "complex_logic", "advanced_math", "complex_puzzles"
            ],
            "topics": [
                "logical_deduction", "arithmetic", "geometry", "probability",
                "algebra", "calculus", "paradoxes", "optimization"
            ]
        }