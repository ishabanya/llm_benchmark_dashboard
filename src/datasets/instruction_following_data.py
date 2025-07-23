"""Instruction following test dataset."""

from typing import List, Dict, Any

from .base import Dataset, TestCaseLoader
from evaluators.base import TestCase


class InstructionFollowingDataset(Dataset):
    """Dataset for instruction following evaluation."""
    
    def __init__(self):
        super().__init__("instruction_following", "instruction_following")
    
    def get_test_cases(self) -> List[TestCase]:
        """Get all instruction following test cases."""
        test_cases = []
        
        # Easy instruction following tasks
        easy_cases = [
            {
                "id": "instruct_easy_001",
                "subcategory": "simple_formatting",
                "difficulty": "easy",
                "prompt": "Write a brief summary of photosynthesis in exactly 50 words.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "word_count": {"target": 50, "tolerance": 0.1}
                    }
                },
                "metadata": {"instruction_type": "word_count", "topic": "science"}
            },
            {
                "id": "instruct_easy_002",
                "subcategory": "simple_formatting",
                "difficulty": "easy",
                "prompt": "List 5 benefits of exercise using bullet points.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "structure": {"type": "bullet_points", "min_items": 5}
                    }
                },
                "metadata": {"instruction_type": "bullet_list", "topic": "health"}
            },
            {
                "id": "instruct_easy_003",
                "subcategory": "simple_tasks",
                "difficulty": "easy",
                "prompt": "Explain what machine learning is, but write your response in a casual, conversational tone.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "tone": {"style": "casual"}
                    }
                },
                "metadata": {"instruction_type": "tone", "topic": "technology"}
            },
            {
                "id": "instruct_easy_004",
                "subcategory": "simple_tasks",
                "difficulty": "easy",
                "prompt": "Write a formal email to a professor asking for a meeting. Include a subject line.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "tone": {"style": "formal"},
                        "structure": {"type": "sections", "sections": ["subject", "greeting", "body", "closing"]}
                    }
                },
                "metadata": {"instruction_type": "email_format", "topic": "communication"}
            },
            {
                "id": "instruct_easy_005",
                "subcategory": "content_constraints",
                "difficulty": "easy",
                "prompt": "Describe the water cycle. Make sure to include the terms 'evaporation', 'condensation', and 'precipitation'.",
                "evaluation_criteria": {
                    "constraints": [
                        {"type": "include_keywords", "keywords": ["evaporation", "condensation", "precipitation"]}
                    ]
                },
                "metadata": {"instruction_type": "keyword_inclusion", "topic": "science"}
            }
        ]
        
        # Medium instruction following tasks
        medium_cases = [
            {
                "id": "instruct_medium_001",
                "subcategory": "multi_step_tasks",
                "difficulty": "medium",
                "prompt": "1. Define artificial intelligence. 2. List 3 types of AI. 3. Explain one potential benefit and one potential risk. 4. Write your response in exactly 4 paragraphs, one for each point.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "structure": {"type": "numbered_list", "min_items": 4},
                        "word_count": {"target": 200, "tolerance": 0.3}
                    },
                    "constraints": [
                        {"type": "min_length", "min_words": 150}
                    ]
                },
                "metadata": {"instruction_type": "multi_step", "topic": "AI"}
            },
            {
                "id": "instruct_medium_002",
                "subcategory": "complex_formatting",
                "difficulty": "medium",
                "prompt": "Create a comparison between dogs and cats. Format your response as a table with 3 categories: physical traits, behavior, and care requirements. Use exactly 2 points per category for each animal.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "structure": {"type": "table", "categories": 3}
                    },
                    "constraints": [
                        {"type": "include_keywords", "keywords": ["physical traits", "behavior", "care requirements"]}
                    ]
                },
                "metadata": {"instruction_type": "table_format", "topic": "animals"}
            },
            {
                "id": "instruct_medium_003",
                "subcategory": "constrained_writing",
                "difficulty": "medium",
                "prompt": "Write a product review for a smartphone. Your review must be between 100-150 words, include at least 2 pros and 2 cons, and end with a numerical rating out of 10.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "word_count": {"target": 125, "tolerance": 0.2}
                    },
                    "constraints": [
                        {"type": "include_keywords", "keywords": ["pros", "cons", "rating"]},
                        {"type": "min_length", "min_words": 100},
                        {"type": "max_length", "max_words": 150}
                    ]
                },
                "metadata": {"instruction_type": "constrained_review", "topic": "technology"}
            },
            {
                "id": "instruct_medium_004",
                "subcategory": "role_specific_tasks",
                "difficulty": "medium",
                "prompt": "You are a travel agent. Create an itinerary for a 3-day trip to Paris. Include activities for each day, estimated costs, and transportation details. Format this as a day-by-day breakdown.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "structure": {"type": "sections", "sections": ["day 1", "day 2", "day 3"]}
                    },
                    "constraints": [
                        {"type": "include_keywords", "keywords": ["activities", "costs", "transportation"]}
                    ]
                },
                "metadata": {"instruction_type": "role_play", "topic": "travel"}
            },
            {
                "id": "instruct_medium_005",
                "subcategory": "analytical_tasks",
                "difficulty": "medium",
                "prompt": "Analyze the pros and cons of remote work. Structure your analysis with: 1) Introduction (1 paragraph), 2) Advantages (3 bullet points), 3) Disadvantages (3 bullet points), 4) Conclusion with your recommendation (1 paragraph).",
                "evaluation_criteria": {
                    "format_requirements": {
                        "structure": {"type": "sections", "sections": ["introduction", "advantages", "disadvantages", "conclusion"]}
                    }
                },
                "metadata": {"instruction_type": "analytical_structure", "topic": "work"}
            }
        ]
        
        # Hard instruction following tasks
        hard_cases = [
            {
                "id": "instruct_hard_001",
                "subcategory": "complex_multi_step",
                "difficulty": "hard",
                "prompt": "Create a comprehensive business plan outline for a food truck. Your response must: 1) Be exactly 300 words, 2) Include 6 main sections with subpoints, 3) Use formal business language, 4) Avoid mentioning specific food types, 5) Include at least one financial term in each section, 6) End with a call to action.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "word_count": {"target": 300, "tolerance": 0.05},
                        "tone": {"style": "formal"},
                        "structure": {"type": "sections", "sections": ["executive summary", "market analysis", "operations", "marketing", "financial projections", "conclusion"]}
                    },
                    "constraints": [
                        {"type": "exclude_keywords", "keywords": ["pizza", "burger", "taco", "sandwich", "chinese", "italian"]},
                        {"type": "include_keywords", "keywords": ["revenue", "cost", "profit", "investment", "budget", "ROI"]}
                    ]
                },
                "metadata": {"instruction_type": "complex_business", "topic": "business"}
            },
            {
                "id": "instruct_hard_002",
                "subcategory": "technical_specifications",
                "difficulty": "hard",
                "prompt": "Write a technical documentation page for a REST API endpoint. Include: HTTP method, URL pattern, request parameters (3 required, 2 optional), response format (JSON schema), error codes (3 different), and a code example in Python. Format using markdown headers and code blocks.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "structure": {"type": "sections", "sections": ["method", "url", "parameters", "response", "errors", "example"]}
                    },
                    "constraints": [
                        {"type": "include_keywords", "keywords": ["HTTP", "JSON", "parameters", "error codes", "Python"]}
                    ]
                },
                "metadata": {"instruction_type": "technical_docs", "topic": "programming"}
            },
            {
                "id": "instruct_hard_003",
                "subcategory": "creative_constraints",
                "difficulty": "hard",
                "prompt": "Write a short story (200-250 words) about time travel, but with these constraints: 1) Never use the words 'time', 'past', 'future', or 'travel', 2) The story must be told in second person ('you'), 3) Include dialogue from exactly 2 characters, 4) The story must have a twist ending, 5) Use present tense throughout.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "word_count": {"target": 225, "tolerance": 0.11}
                    },
                    "constraints": [
                        {"type": "exclude_keywords", "keywords": ["time", "past", "future", "travel"]},
                        {"type": "include_keywords", "keywords": ["you", "dialogue", "twist"]}
                    ]
                },
                "metadata": {"instruction_type": "creative_constraints", "topic": "creative_writing"}
            },
            {
                "id": "instruct_hard_004",
                "subcategory": "academic_formatting",
                "difficulty": "hard",
                "prompt": "Write an abstract for a fictional research paper on the effects of social media on teenagers. Follow APA format: 150-250 words, include background, methods, results, and conclusions sections. Use academic language, include 2 statistical findings, and ensure it's written in past tense for completed research.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "word_count": {"target": 200, "tolerance": 0.25},
                        "structure": {"type": "sections", "sections": ["background", "methods", "results", "conclusions"]},
                        "tone": {"style": "academic"}
                    },
                    "constraints": [
                        {"type": "include_keywords", "keywords": ["statistical", "research", "methodology"]},
                        {"type": "min_length", "min_words": 150},
                        {"type": "max_length", "max_words": 250}
                    ]
                },
                "metadata": {"instruction_type": "academic_abstract", "topic": "research"}
            },
            {
                "id": "instruct_hard_005",
                "subcategory": "multi_format_integration",
                "difficulty": "hard",
                "prompt": "Create a product launch announcement that includes: 1) A catchy headline (max 10 words), 2) An executive summary (50 words), 3) Key features (5 bullet points), 4) Target audience analysis (2 paragraphs), 5) A pricing table (3 tiers), 6) A call-to-action (1 sentence). Total length: 400-450 words. Use marketing language but avoid superlatives like 'best', 'perfect', 'amazing'.",
                "evaluation_criteria": {
                    "format_requirements": {
                        "word_count": {"target": 425, "tolerance": 0.06},
                        "structure": {"type": "sections", "sections": ["headline", "summary", "features", "audience", "pricing", "call-to-action"]}
                    },
                    "constraints": [
                        {"type": "exclude_keywords", "keywords": ["best", "perfect", "amazing", "incredible", "outstanding"]},
                        {"type": "min_length", "min_words": 400},
                        {"type": "max_length", "max_words": 450}
                    ]
                },
                "metadata": {"instruction_type": "marketing_complex", "topic": "marketing"}
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
                expected_answer=case_data.get("expected_answer"),
                evaluation_criteria=case_data.get("evaluation_criteria", {}),
                metadata=case_data.get("metadata", {})
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get dataset metadata."""
        return {
            "name": self.name,
            "category": self.category,
            "description": "Tests ability to follow complex, multi-step instructions with various constraints",
            "total_cases": 15,
            "difficulty_distribution": {
                "easy": 5,
                "medium": 5,
                "hard": 5
            },
            "subcategories": [
                "simple_formatting", "simple_tasks", "content_constraints",
                "multi_step_tasks", "complex_formatting", "constrained_writing",
                "role_specific_tasks", "analytical_tasks", "complex_multi_step",
                "technical_specifications", "creative_constraints", "academic_formatting",
                "multi_format_integration"
            ],
            "constraint_types": [
                "word_count", "formatting", "tone", "keyword_inclusion", "keyword_exclusion",
                "structure", "role_playing", "technical_requirements"
            ]
        }