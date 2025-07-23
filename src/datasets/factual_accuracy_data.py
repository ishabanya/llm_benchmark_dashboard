"""Factual accuracy test dataset."""

from typing import List, Dict, Any

from .base import Dataset, TestCaseLoader
from evaluators.base import TestCase


class FactualAccuracyDataset(Dataset):
    """Dataset for factual accuracy evaluation."""
    
    def __init__(self):
        super().__init__("factual_accuracy", "factual_accuracy")
    
    def get_test_cases(self) -> List[TestCase]:
        """Get all factual accuracy test cases."""
        test_cases = []
        
        # Easy questions - basic facts
        easy_cases = [
            {
                "id": "fact_easy_001",
                "subcategory": "basic_facts",
                "difficulty": "easy",
                "prompt": "What is the capital of France?",
                "expected_answer": "Paris",
                "metadata": {"topic": "geography", "source": "common_knowledge"}
            },
            {
                "id": "fact_easy_002", 
                "subcategory": "basic_facts",
                "difficulty": "easy",
                "prompt": "Who wrote the play 'Romeo and Juliet'?",
                "expected_answer": "William Shakespeare",
                "metadata": {"topic": "literature", "source": "common_knowledge"}
            },
            {
                "id": "fact_easy_003",
                "subcategory": "basic_facts", 
                "difficulty": "easy",
                "prompt": "What is the chemical symbol for gold?",
                "expected_answer": "Au",
                "metadata": {"topic": "chemistry", "source": "periodic_table"}
            },
            {
                "id": "fact_easy_004",
                "subcategory": "basic_facts",
                "difficulty": "easy", 
                "prompt": "How many continents are there?",
                "expected_answer": "7",
                "metadata": {"topic": "geography", "source": "common_knowledge"}
            },
            {
                "id": "fact_easy_005",
                "subcategory": "basic_facts",
                "difficulty": "easy",
                "prompt": "What year did World War II end?",
                "expected_answer": "1945",
                "metadata": {"topic": "history", "source": "historical_facts"}
            },
            {
                "id": "fact_easy_006",
                "subcategory": "basic_facts",
                "difficulty": "easy",
                "prompt": "What is the largest planet in our solar system?",
                "expected_answer": "Jupiter",
                "metadata": {"topic": "astronomy", "source": "science_facts"}
            },
            {
                "id": "fact_easy_007",
                "subcategory": "basic_facts",
                "difficulty": "easy",
                "prompt": "Who painted the Mona Lisa?",
                "expected_answer": "Leonardo da Vinci",
                "metadata": {"topic": "art", "source": "art_history"}
            },
            {
                "id": "fact_easy_008",
                "subcategory": "basic_facts",
                "difficulty": "easy",
                "prompt": "What is the speed of light in vacuum?",
                "expected_answer": "299,792,458 meters per second",
                "metadata": {"topic": "physics", "source": "scientific_constants"}
            }
        ]
        
        # Medium questions - more specific knowledge
        medium_cases = [
            {
                "id": "fact_medium_001",
                "subcategory": "specific_knowledge",
                "difficulty": "medium",
                "prompt": "What is the atomic number of carbon?",
                "expected_answer": "6",
                "metadata": {"topic": "chemistry", "source": "periodic_table"}
            },
            {
                "id": "fact_medium_002",
                "subcategory": "specific_knowledge", 
                "difficulty": "medium",
                "prompt": "In which year was the Berlin Wall torn down?",
                "expected_answer": "1989",
                "metadata": {"topic": "history", "source": "historical_events"}
            },
            {
                "id": "fact_medium_003",
                "subcategory": "specific_knowledge",
                "difficulty": "medium",
                "prompt": "What is the smallest prime number?",
                "expected_answer": "2",
                "metadata": {"topic": "mathematics", "source": "number_theory"}
            },
            {
                "id": "fact_medium_004",
                "subcategory": "specific_knowledge",
                "difficulty": "medium",
                "prompt": "Which hormone is produced by the pancreas to regulate blood sugar?",
                "expected_answer": "insulin",
                "metadata": {"topic": "biology", "source": "medical_knowledge"}
            },
            {
                "id": "fact_medium_005",
                "subcategory": "specific_knowledge",
                "difficulty": "medium",
                "prompt": "What is the currency of Japan?",
                "expected_answer": "yen",
                "metadata": {"topic": "economics", "source": "currency_facts"}
            },
            {
                "id": "fact_medium_006",
                "subcategory": "specific_knowledge",
                "difficulty": "medium",
                "prompt": "Who developed the theory of evolution by natural selection?",
                "expected_answer": "Charles Darwin",
                "metadata": {"topic": "biology", "source": "scientific_history"}
            },
            {
                "id": "fact_medium_007",
                "subcategory": "specific_knowledge",
                "difficulty": "medium",
                "prompt": "What is the tallest mountain in Africa?",
                "expected_answer": "Mount Kilimanjaro",
                "metadata": {"topic": "geography", "source": "geographical_facts"}
            },
            {
                "id": "fact_medium_008",
                "subcategory": "specific_knowledge",
                "difficulty": "medium",
                "prompt": "In which programming language was the Linux kernel originally written?",
                "expected_answer": "C",
                "metadata": {"topic": "technology", "source": "programming_history"}
            },
            {
                "id": "fact_medium_009",
                "subcategory": "specific_knowledge",
                "difficulty": "medium",
                "prompt": "What is the half-life of Carbon-14?",
                "expected_answer": "5,730 years",
                "metadata": {"topic": "physics", "source": "radioactive_decay"}
            }
        ]
        
        # Hard questions - specialized/detailed knowledge
        hard_cases = [
            {
                "id": "fact_hard_001",
                "subcategory": "specialized_knowledge",
                "difficulty": "hard",
                "prompt": "What is the molecular formula of caffeine?",
                "expected_answer": "C8H10N4O2",
                "metadata": {"topic": "chemistry", "source": "molecular_chemistry"}
            },
            {
                "id": "fact_hard_002",
                "subcategory": "specialized_knowledge",
                "difficulty": "hard", 
                "prompt": "Who was the first person to calculate the circumference of the Earth?",
                "expected_answer": "Eratosthenes",
                "metadata": {"topic": "history", "source": "ancient_science"}
            },
            {
                "id": "fact_hard_003",
                "subcategory": "specialized_knowledge",
                "difficulty": "hard",
                "prompt": "What is the Avogadro constant value?",
                "expected_answer": "6.022 × 10^23 per mole",
                "metadata": {"topic": "chemistry", "source": "physical_constants"}
            },
            {
                "id": "fact_hard_004",
                "subcategory": "specialized_knowledge",
                "difficulty": "hard",
                "prompt": "In which year did the Chernobyl nuclear disaster occur?",
                "expected_answer": "1986",
                "metadata": {"topic": "history", "source": "nuclear_accidents"}
            },
            {
                "id": "fact_hard_005",
                "subcategory": "specialized_knowledge",
                "difficulty": "hard",
                "prompt": "What is the name of the galaxy closest to the Milky Way?",
                "expected_answer": "Andromeda Galaxy",
                "metadata": {"topic": "astronomy", "source": "galactic_astronomy"}
            },
            {
                "id": "fact_hard_006",
                "subcategory": "specialized_knowledge",
                "difficulty": "hard",
                "prompt": "What is the medical term for the collarbone?",
                "expected_answer": "clavicle",
                "metadata": {"topic": "medicine", "source": "anatomy"}
            },
            {
                "id": "fact_hard_007",
                "subcategory": "specialized_knowledge",
                "difficulty": "hard",
                "prompt": "Who invented the World Wide Web?",
                "expected_answer": "Tim Berners-Lee",
                "metadata": {"topic": "technology", "source": "internet_history"}
            },
            {
                "id": "fact_hard_008",
                "subcategory": "specialized_knowledge",
                "difficulty": "hard",
                "prompt": "What is the rarest naturally occurring element on Earth?",
                "expected_answer": "astatine",
                "metadata": {"topic": "chemistry", "source": "element_rarity"}
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
            "description": "Tests factual accuracy across various domains",
            "total_cases": 25,
            "difficulty_distribution": {
                "easy": 8,
                "medium": 9,
                "hard": 8
            },
            "subcategories": [
                "basic_facts",
                "specific_knowledge", 
                "specialized_knowledge"
            ],
            "topics": [
                "geography", "literature", "chemistry", "history",
                "astronomy", "art", "physics", "mathematics",
                "biology", "economics", "technology", "medicine"
            ]
        }