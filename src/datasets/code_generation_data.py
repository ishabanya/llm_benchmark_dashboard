"""Code generation test dataset."""

from typing import List, Dict, Any

from .base import Dataset, TestCaseLoader
from evaluators.base import TestCase


class CodeGenerationDataset(Dataset):
    """Dataset for code generation evaluation."""
    
    def __init__(self):
        super().__init__("code_generation", "code_generation")
    
    def get_test_cases(self) -> List[TestCase]:
        """Get all code generation test cases."""
        test_cases = []
        
        # Easy code generation tasks
        easy_cases = [
            {
                "id": "code_easy_001",
                "subcategory": "basic_functions",
                "difficulty": "easy",
                "prompt": "Write a Python function that takes two numbers and returns their sum.",
                "expected_answer": "def add_numbers(a, b):\n    return a + b",
                "evaluation_criteria": {
                    "test_cases": [
                        {"input": "add_numbers(2, 3)", "expected_output": "5"},
                        {"input": "add_numbers(-1, 1)", "expected_output": "0"},
                        {"input": "add_numbers(0, 0)", "expected_output": "0"}
                    ]
                }
            },
            {
                "id": "code_easy_002", 
                "subcategory": "basic_functions",
                "difficulty": "easy",
                "prompt": "Create a function that checks if a number is even.",
                "expected_answer": "def is_even(n):\n    return n % 2 == 0",
                "evaluation_criteria": {
                    "test_cases": [
                        {"input": "is_even(4)", "expected_output": "True"},
                        {"input": "is_even(7)", "expected_output": "False"},
                        {"input": "is_even(0)", "expected_output": "True"}
                    ]
                }
            },
            {
                "id": "code_easy_003",
                "subcategory": "string_manipulation",
                "difficulty": "easy",
                "prompt": "Write a function that reverses a string.",
                "expected_answer": "def reverse_string(s):\n    return s[::-1]",
                "evaluation_criteria": {
                    "test_cases": [
                        {"input": "reverse_string('hello')", "expected_output": "'olleh'"},
                        {"input": "reverse_string('Python')", "expected_output": "'nohtyP'"}
                    ]
                }
            },
            {
                "id": "code_easy_004",
                "subcategory": "loops",
                "difficulty": "easy",
                "prompt": "Write a function that calculates the factorial of a number using a loop.",
                "expected_answer": "def factorial(n):\n    result = 1\n    for i in range(1, n + 1):\n        result *= i\n    return result",
                "evaluation_criteria": {
                    "test_cases": [
                        {"input": "factorial(5)", "expected_output": "120"},
                        {"input": "factorial(0)", "expected_output": "1"}
                    ]
                }
            },
            {
                "id": "code_easy_005",
                "subcategory": "list_operations",
                "difficulty": "easy",
                "prompt": "Create a function that finds the maximum number in a list.",
                "expected_answer": "def find_max(lst):\n    return max(lst)",
                "evaluation_criteria": {
                    "test_cases": [
                        {"input": "find_max([1, 5, 3, 9, 2])", "expected_output": "9"},
                        {"input": "find_max([-1, -5, -2])", "expected_output": "-1"}
                    ]
                }
            }
        ]
        
        # Medium code generation tasks
        medium_cases = [
            {
                "id": "code_medium_001",
                "subcategory": "algorithms",
                "difficulty": "medium",
                "prompt": "Implement a binary search function for a sorted list.",
                "expected_answer": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1",
                "evaluation_criteria": {
                    "test_cases": [
                        {"input": "binary_search([1, 3, 5, 7, 9], 5)", "expected_output": "2"},
                        {"input": "binary_search([1, 3, 5, 7, 9], 6)", "expected_output": "-1"}
                    ]
                }
            },
            {
                "id": "code_medium_002",
                "subcategory": "data_structures",
                "difficulty": "medium",
                "prompt": "Create a class representing a simple stack with push, pop, and peek operations.",
                "expected_answer": "class Stack:\n    def __init__(self):\n        self.items = []\n    \n    def push(self, item):\n        self.items.append(item)\n    \n    def pop(self):\n        if self.items:\n            return self.items.pop()\n        return None\n    \n    def peek(self):\n        if self.items:\n            return self.items[-1]\n        return None",
                "evaluation_criteria": {
                    "test_cases": [
                        {"input": "s = Stack(); s.push(1); s.push(2); s.pop()", "expected_output": "2"},
                        {"input": "s = Stack(); s.push(5); s.peek()", "expected_output": "5"}
                    ]
                }
            },
            {
                "id": "code_medium_003",
                "subcategory": "string_processing",
                "difficulty": "medium",
                "prompt": "Write a function that checks if a string is a palindrome (ignoring spaces and case).",
                "expected_answer": "def is_palindrome(s):\n    cleaned = ''.join(s.split()).lower()\n    return cleaned == cleaned[::-1]",
                "evaluation_criteria": {
                    "test_cases": [
                        {"input": "is_palindrome('A man a plan a canal Panama')", "expected_output": "True"},
                        {"input": "is_palindrome('race a car')", "expected_output": "False"}
                    ]
                }
            },
            {
                "id": "code_medium_004",
                "subcategory": "file_handling",
                "difficulty": "medium",
                "prompt": "Create a function that reads a text file and counts word frequencies.",
                "expected_answer": "def count_words(filename):\n    word_count = {}\n    with open(filename, 'r') as file:\n        for line in file:\n            words = line.strip().split()\n            for word in words:\n                word = word.lower().strip('.,!?')\n                word_count[word] = word_count.get(word, 0) + 1\n    return word_count",
                "evaluation_criteria": {"requires_file_handling": True}
            },
            {
                "id": "code_medium_005",
                "subcategory": "recursion",
                "difficulty": "medium",
                "prompt": "Implement the Fibonacci sequence using recursion with memoization.",
                "expected_answer": "def fibonacci(n, memo={}):\n    if n in memo:\n        return memo[n]\n    if n <= 1:\n        return n\n    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)\n    return memo[n]",
                "evaluation_criteria": {
                    "test_cases": [
                        {"input": "fibonacci(10)", "expected_output": "55"},
                        {"input": "fibonacci(0)", "expected_output": "0"}
                    ]
                }
            }
        ]
        
        # Hard code generation tasks
        hard_cases = [
            {
                "id": "code_hard_001",
                "subcategory": "advanced_algorithms",
                "difficulty": "hard",
                "prompt": "Implement a function to find the longest common subsequence between two strings.",
                "expected_answer": "def lcs(s1, s2):\n    m, n = len(s1), len(s2)\n    dp = [[0] * (n + 1) for _ in range(m + 1)]\n    \n    for i in range(1, m + 1):\n        for j in range(1, n + 1):\n            if s1[i-1] == s2[j-1]:\n                dp[i][j] = dp[i-1][j-1] + 1\n            else:\n                dp[i][j] = max(dp[i-1][j], dp[i][j-1])\n    \n    return dp[m][n]",
                "evaluation_criteria": {
                    "test_cases": [
                        {"input": "lcs('ABCDGH', 'AEDFHR')", "expected_output": "3"},
                        {"input": "lcs('AGGTAB', 'GXTXAYB')", "expected_output": "4"}
                    ]
                }
            },
            {
                "id": "code_hard_002",
                "subcategory": "design_patterns",
                "difficulty": "hard",
                "prompt": "Implement a Singleton pattern in Python with thread safety.",
                "expected_answer": "import threading\n\nclass Singleton:\n    _instance = None\n    _lock = threading.Lock()\n    \n    def __new__(cls):\n        if cls._instance is None:\n            with cls._lock:\n                if cls._instance is None:\n                    cls._instance = super().__new__(cls)\n        return cls._instance",
                "evaluation_criteria": {"thread_safety": True, "singleton_pattern": True}
            },
            {
                "id": "code_hard_003",
                "subcategory": "advanced_data_structures",
                "difficulty": "hard",
                "prompt": "Implement a Trie (prefix tree) data structure with insert, search, and startsWith methods.",
                "expected_answer": "class TrieNode:\n    def __init__(self):\n        self.children = {}\n        self.is_end = False\n\nclass Trie:\n    def __init__(self):\n        self.root = TrieNode()\n    \n    def insert(self, word):\n        node = self.root\n        for char in word:\n            if char not in node.children:\n                node.children[char] = TrieNode()\n            node = node.children[char]\n        node.is_end = True\n    \n    def search(self, word):\n        node = self.root\n        for char in word:\n            if char not in node.children:\n                return False\n            node = node.children[char]\n        return node.is_end\n    \n    def startsWith(self, prefix):\n        node = self.root\n        for char in prefix:\n            if char not in node.children:\n                return False\n            node = node.children[char]\n        return True",
                "evaluation_criteria": {
                    "test_cases": [
                        {"input": "trie = Trie(); trie.insert('apple'); trie.search('apple')", "expected_output": "True"},
                        {"input": "trie.startsWith('app')", "expected_output": "True"}
                    ]
                }
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
            "description": "Tests Python code generation capabilities",
            "total_cases": 13,
            "difficulty_distribution": {
                "easy": 5,
                "medium": 5,
                "hard": 3
            },
            "subcategories": [
                "basic_functions", "string_manipulation", "loops", "list_operations",
                "algorithms", "data_structures", "string_processing", "file_handling",
                "recursion", "advanced_algorithms", "design_patterns", "advanced_data_structures"
            ]
        }