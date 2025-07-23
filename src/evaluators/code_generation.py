"""Code generation evaluator."""

import ast
import re
import subprocess
import tempfile
import os
from typing import Any, Dict, List

from .base import Evaluator, TestCase, EvaluationResult
from models.base import ModelResponse


class CodeGenerationEvaluator(Evaluator):
    """Evaluates code generation quality and correctness."""
    
    def __init__(self):
        super().__init__("code_generation")
    
    async def evaluate(
        self, 
        test_case: TestCase, 
        response: ModelResponse
    ) -> EvaluationResult:
        """Evaluate code generation quality."""
        try:
            actual_code = self._extract_code(response.content)
            
            if not actual_code:
                return self.create_result(
                    test_case, response, 0, 100,
                    {"error": "No code found in response"},
                    "No code extracted from response"
                )
            
            scores = {}
            
            # 1. Syntax correctness
            scores["syntax_correctness"] = self._check_syntax(actual_code)
            
            # 2. Functionality (if test cases provided)
            scores["functionality"] = await self._test_functionality(
                actual_code, test_case.evaluation_criteria
            )
            
            # 3. Code quality
            scores["code_quality"] = self._evaluate_code_quality(actual_code)
            
            # 4. Best practices
            scores["best_practices"] = self._check_best_practices(actual_code)
            
            # 5. Documentation
            scores["documentation"] = self._check_documentation(actual_code)
            
            # Calculate weighted final score
            weights = {
                "syntax_correctness": 0.3,
                "functionality": 0.35,
                "code_quality": 0.15,
                "best_practices": 0.1,
                "documentation": 0.1
            }
            
            final_score = sum(scores[key] * weights[key] for key in scores)
            
            evaluation_details = {
                "extracted_code": actual_code,
                "component_scores": scores,
                "weights": weights,
                "final_score": final_score,
                "code_metrics": self._get_code_metrics(actual_code)
            }
            
            return self.create_result(
                test_case, response, final_score, 100, evaluation_details
            )
            
        except Exception as e:
            return self.create_result(
                test_case, response, 0, 100,
                {"error": str(e)}, f"Evaluation error: {str(e)}"
            )
    
    def _extract_code(self, text: str) -> str:
        """Extract Python code from the response."""
        # Look for code blocks
        code_block_pattern = r'```(?:python)?\n?(.*?)```'
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Look for indented code blocks
        lines = text.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                in_code = True
                code_lines.append(line)
            elif in_code and (line.startswith('    ') or line.strip() == ''):
                code_lines.append(line)
            elif in_code and not line.startswith('    ') and line.strip():
                break
        
        if code_lines:
            return '\n'.join(code_lines)
        
        # Fallback: look for function definitions
        func_pattern = r'(def\s+\w+.*?(?=def\s+\w+|class\s+\w+|$))'
        matches = re.findall(func_pattern, text, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        return text.strip()
    
    def _check_syntax(self, code: str) -> float:
        """Check if the code has valid Python syntax."""
        try:
            ast.parse(code)
            return 100.0
        except SyntaxError as e:
            # Partial credit based on error location
            lines = code.split('\n')
            if hasattr(e, 'lineno') and e.lineno:
                error_line = e.lineno
                total_lines = len(lines)
                # Give partial credit based on how much code is valid
                valid_ratio = max(0, (error_line - 1) / total_lines)
                return valid_ratio * 50  # Max 50% for partial syntax
            return 0.0
        except Exception:
            return 0.0
    
    async def _test_functionality(
        self, 
        code: str, 
        criteria: Dict[str, Any]
    ) -> float:
        """Test code functionality against test cases."""
        if not criteria or "test_cases" not in criteria:
            return 100.0  # No tests to run
        
        test_cases = criteria["test_cases"]
        if not test_cases:
            return 100.0
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for test_case in test_cases:
            try:
                if await self._run_test_case(code, test_case):
                    passed_tests += 1
            except Exception:
                continue
        
        return (passed_tests / total_tests) * 100.0 if total_tests > 0 else 100.0
    
    async def _run_test_case(self, code: str, test_case: Dict[str, Any]) -> bool:
        """Run a single test case."""
        try:
            # Create temporary file with the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.write('\n\n')
                
                # Add test code
                if "input" in test_case and "expected_output" in test_case:
                    test_code = f"""
# Test case
try:
    result = {test_case["input"]}
    expected = {test_case["expected_output"]}
    if result == expected:
        print("PASS")
    else:
        print(f"FAIL: got {{result}}, expected {{expected}}")
except Exception as e:
    print(f"ERROR: {{e}}")
"""
                    f.write(test_code)
                
                temp_file = f.name
            
            # Run the code
            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return "PASS" in result.stdout
            
        except Exception:
            return False
    
    def _evaluate_code_quality(self, code: str) -> float:
        """Evaluate overall code quality."""
        score = 0.0
        
        # Check for proper naming conventions
        if re.search(r'def\s+[a-z_][a-z0-9_]*\s*\(', code):
            score += 20  # Function naming
        
        if re.search(r'class\s+[A-Z][a-zA-Z0-9]*\s*[:\(]', code):
            score += 10  # Class naming
        
        # Check for proper spacing
        if '=' in code and re.search(r'\w\s*=\s*\w', code):
            score += 15  # Assignment spacing
        
        if ',' in code and re.search(r',\s+', code):
            score += 10  # Comma spacing
        
        # Check for error handling
        if 'try:' in code and 'except' in code:
            score += 20  # Error handling
        
        # Check for type hints (bonus)
        if re.search(r':\s*\w+', code):
            score += 15  # Type hints
        
        # Check for reasonable line length
        lines = code.split('\n')
        long_lines = sum(1 for line in lines if len(line) > 100)
        if long_lines == 0:
            score += 10  # No overly long lines
        
        return min(100.0, score)
    
    def _check_best_practices(self, code: str) -> float:
        """Check for Python best practices."""
        score = 0.0
        
        # Check for main guard
        if 'if __name__ == "__main__":' in code:
            score += 25
        
        # Check for imports at top
        lines = code.strip().split('\n')
        import_lines = [i for i, line in enumerate(lines) if line.strip().startswith(('import ', 'from '))]
        if import_lines and all(i < 5 for i in import_lines):
            score += 20
        
        # Check for no global variables (except constants)
        global_vars = re.findall(r'^[a-z_][a-z0-9_]*\s*=', code, re.MULTILINE)
        if len(global_vars) <= 2:  # Allow some constants
            score += 20
        
        # Check for list comprehensions over loops (when appropriate)
        if '[' in code and 'for' in code and ']' in code:
            if code.count('[') > code.count('for i in range'):
                score += 15
        
        # Check for f-strings over format()
        if 'f"' in code or "f'" in code:
            score += 10
        elif '.format(' in code or '%' in code:
            score += 5
        
        # Check for descriptive variable names
        vars_found = re.findall(r'\b[a-z_][a-z0-9_]*\b', code)
        descriptive_vars = [v for v in vars_found if len(v) > 2 and v not in ['for', 'def', 'try', 'if']]
        if len(descriptive_vars) > len(vars_found) * 0.7:
            score += 10
        
        return min(100.0, score)
    
    def _check_documentation(self, code: str) -> float:
        """Check for code documentation."""
        score = 0.0
        
        # Check for docstrings
        if '"""' in code or "'''" in code:
            score += 50
        
        # Check for comments
        comment_lines = [line for line in code.split('\n') if line.strip().startswith('#')]
        total_lines = len([line for line in code.split('\n') if line.strip()])
        
        if total_lines > 0:
            comment_ratio = len(comment_lines) / total_lines
            if comment_ratio > 0.1:
                score += 30
            elif comment_ratio > 0.05:
                score += 20
            elif comment_ratio > 0:
                score += 10
        
        # Check for inline comments
        inline_comments = len(re.findall(r'#.*$', code, re.MULTILINE))
        if inline_comments > 0:
            score += 20
        
        return min(100.0, score)
    
    def _get_code_metrics(self, code: str) -> Dict[str, Any]:
        """Get various code metrics."""
        lines = code.split('\n')
        
        return {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "functions": len(re.findall(r'def\s+\w+', code)),
            "classes": len(re.findall(r'class\s+\w+', code)),
            "imports": len(re.findall(r'^(?:import|from)\s+', code, re.MULTILINE)),
            "has_docstrings": '"""' in code or "'''" in code,
            "has_type_hints": ':' in code and '->' in code
        }
    
    def get_evaluation_criteria(self) -> Dict[str, Any]:
        """Get evaluation criteria for code generation."""
        return {
            "name": "Code Generation",
            "description": "Evaluates Python code quality and correctness",
            "scoring_components": {
                "syntax_correctness": "Valid Python syntax (30%)",
                "functionality": "Code works as expected (35%)",
                "code_quality": "Code quality and style (15%)",
                "best_practices": "Python best practices (10%)",
                "documentation": "Comments and docstrings (10%)"
            },
            "passing_threshold": 70.0,
            "max_score": 100.0
        }