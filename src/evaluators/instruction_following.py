"""Instruction following evaluator."""

import re
from typing import Any, Dict, List

from .base import Evaluator, TestCase, EvaluationResult
from models.base import ModelResponse


class InstructionFollowingEvaluator(Evaluator):
    """Evaluates how well the model follows complex instructions."""
    
    def __init__(self):
        super().__init__("instruction_following")
    
    async def evaluate(
        self, 
        test_case: TestCase, 
        response: ModelResponse
    ) -> EvaluationResult:
        """Evaluate instruction following capability."""
        try:
            instructions = self._parse_instructions(test_case.prompt)
            response_content = response.content
            
            scores = {}
            
            # 1. Completeness - did it address all parts?
            scores["completeness"] = self._check_completeness(instructions, response_content)
            
            # 2. Format compliance
            scores["format_compliance"] = self._check_format_compliance(
                test_case.evaluation_criteria, response_content
            )
            
            # 3. Order adherence
            scores["order_adherence"] = self._check_order_adherence(instructions, response_content)
            
            # 4. Constraint satisfaction
            scores["constraint_satisfaction"] = self._check_constraints(
                test_case.evaluation_criteria, response_content
            )
            
            # 5. Detail level appropriateness
            scores["detail_level"] = self._check_detail_level(
                test_case.evaluation_criteria, response_content
            )
            
            # Calculate weighted final score
            weights = {
                "completeness": 0.3,
                "format_compliance": 0.25,
                "order_adherence": 0.2,
                "constraint_satisfaction": 0.15,
                "detail_level": 0.1
            }
            
            final_score = sum(scores[key] * weights[key] for key in scores)
            
            evaluation_details = {
                "parsed_instructions": instructions,
                "component_scores": scores,
                "weights": weights,
                "final_score": final_score,
                "instruction_analysis": self._analyze_instructions(test_case.prompt),
                "response_analysis": self._analyze_response(response_content)
            }
            
            return self.create_result(
                test_case, response, final_score, 100, evaluation_details
            )
            
        except Exception as e:
            return self.create_result(
                test_case, response, 0, 100,
                {"error": str(e)}, f"Evaluation error: {str(e)}"
            )
    
    def _parse_instructions(self, prompt: str) -> List[Dict[str, Any]]:
        """Parse individual instructions from the prompt."""
        instructions = []
        
        # Look for numbered instructions
        numbered_pattern = r'(\d+\.)\s*([^0-9]*?)(?=\d+\.|$)'
        numbered_matches = re.findall(numbered_pattern, prompt, re.DOTALL)
        
        if numbered_matches:
            for i, (number, instruction) in enumerate(numbered_matches):
                instructions.append({
                    "order": i + 1,
                    "number": number,
                    "text": instruction.strip(),
                    "type": "numbered"
                })
        else:
            # Look for bullet points
            bullet_pattern = r'[•\-\*]\s*([^\n•\-\*]*)'
            bullet_matches = re.findall(bullet_pattern, prompt)
            
            if bullet_matches:
                for i, instruction in enumerate(bullet_matches):
                    instructions.append({
                        "order": i + 1,
                        "text": instruction.strip(),
                        "type": "bullet"
                    })
            else:
                # Look for imperative sentences
                sentences = re.split(r'[.!?]+', prompt)
                for i, sentence in enumerate(sentences):
                    sentence = sentence.strip()
                    if sentence and self._is_instruction(sentence):
                        instructions.append({
                            "order": i + 1,
                            "text": sentence,
                            "type": "imperative"
                        })
        
        return instructions
    
    def _is_instruction(self, sentence: str) -> bool:
        """Check if a sentence is likely an instruction."""
        instruction_verbs = [
            "write", "create", "make", "generate", "produce", "develop",
            "explain", "describe", "analyze", "compare", "summarize",
            "list", "identify", "find", "calculate", "solve", "determine",
            "include", "provide", "give", "show", "demonstrate", "ensure"
        ]
        
        words = sentence.lower().split()
        if not words:
            return False
        
        return any(verb in words[:3] for verb in instruction_verbs)
    
    def _check_completeness(self, instructions: List[Dict[str, Any]], response: str) -> float:
        """Check if all instructions were addressed."""
        if not instructions:
            return 100.0
        
        addressed_count = 0
        
        for instruction in instructions:
            if self._instruction_addressed(instruction, response):
                addressed_count += 1
        
        return (addressed_count / len(instructions)) * 100.0
    
    def _instruction_addressed(self, instruction: Dict[str, Any], response: str) -> bool:
        """Check if a specific instruction was addressed in the response."""
        instruction_text = instruction["text"].lower()
        response_lower = response.lower()
        
        # Extract key action words
        action_words = re.findall(r'\b(?:write|create|make|generate|explain|describe|analyze|list|include|provide|calculate|solve|determine)\b', instruction_text)
        
        # Check if key concepts from instruction appear in response
        instruction_words = set(instruction_text.split())
        response_words = set(response_lower.split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must'}
        
        instruction_keywords = instruction_words - common_words
        response_keywords = response_words - common_words
        
        if not instruction_keywords:
            return True  # Nothing specific to check
        
        # Calculate keyword overlap
        overlap = len(instruction_keywords.intersection(response_keywords))
        overlap_ratio = overlap / len(instruction_keywords)
        
        return overlap_ratio >= 0.3  # At least 30% keyword overlap
    
    def _check_format_compliance(self, criteria: Dict[str, Any], response: str) -> float:
        """Check compliance with format requirements."""
        if not criteria or "format_requirements" not in criteria:
            return 100.0
        
        format_reqs = criteria["format_requirements"]
        score = 0.0
        total_checks = 0
        
        # Check specific format requirements
        for req_type, requirement in format_reqs.items():
            total_checks += 1
            
            if req_type == "word_count":
                actual_count = len(response.split())
                target_count = requirement.get("target", 0)
                tolerance = requirement.get("tolerance", 0.2)
                
                if target_count > 0:
                    lower_bound = target_count * (1 - tolerance)
                    upper_bound = target_count * (1 + tolerance)
                    
                    if lower_bound <= actual_count <= upper_bound:
                        score += 100
                    else:
                        # Partial credit based on how close it is
                        distance = min(abs(actual_count - lower_bound), abs(actual_count - upper_bound))
                        relative_distance = distance / target_count
                        score += max(0, 100 - (relative_distance * 100))
            
            elif req_type == "structure":
                structure_type = requirement.get("type", "")
                
                if structure_type == "sections":
                    required_sections = requirement.get("sections", [])
                    found_sections = 0
                    
                    for section in required_sections:
                        if section.lower() in response.lower():
                            found_sections += 1
                    
                    if required_sections:
                        score += (found_sections / len(required_sections)) * 100
                    else:
                        score += 100
                
                elif structure_type == "numbered_list":
                    numbered_items = len(re.findall(r'\d+\.', response))
                    expected_items = requirement.get("min_items", 1)
                    
                    if numbered_items >= expected_items:
                        score += 100
                    else:
                        score += (numbered_items / expected_items) * 100
                
                elif structure_type == "bullet_points":
                    bullet_items = len(re.findall(r'[•\-\*]', response))
                    expected_items = requirement.get("min_items", 1)
                    
                    if bullet_items >= expected_items:
                        score += 100
                    else:
                        score += (bullet_items / expected_items) * 100
            
            elif req_type == "tone":
                expected_tone = requirement.get("style", "").lower()
                
                if expected_tone == "formal":
                    # Check for formal language indicators
                    formal_indicators = ["furthermore", "however", "therefore", "moreover", "nonetheless"]
                    informal_indicators = ["gonna", "wanna", "yeah", "ok", "hey"]
                    
                    formal_count = sum(1 for indicator in formal_indicators if indicator in response.lower())
                    informal_count = sum(1 for indicator in informal_indicators if indicator in response.lower())
                    
                    if informal_count == 0 and formal_count > 0:
                        score += 100
                    elif informal_count == 0:
                        score += 70
                    else:
                        score += max(0, 70 - (informal_count * 20))
                
                elif expected_tone == "casual":
                    # Check for casual language
                    casual_indicators = ["you", "your", "let's", "we'll", "here's"]
                    casual_count = sum(1 for indicator in casual_indicators if indicator in response.lower())
                    
                    if casual_count >= 2:
                        score += 100
                    elif casual_count >= 1:
                        score += 70
                    else:
                        score += 40
        
        return score / total_checks if total_checks > 0 else 100.0
    
    def _check_order_adherence(self, instructions: List[Dict[str, Any]], response: str) -> float:
        """Check if instructions were followed in the correct order."""
        if len(instructions) <= 1:
            return 100.0
        
        # Find the order in which topics appear in the response
        response_lower = response.lower()
        instruction_positions = []
        
        for instruction in instructions:
            instruction_text = instruction["text"].lower()
            keywords = [word for word in instruction_text.split() if len(word) > 4]
            
            if keywords:
                # Find first occurrence of instruction keywords
                earliest_pos = len(response)
                for keyword in keywords:
                    pos = response_lower.find(keyword)
                    if pos != -1:
                        earliest_pos = min(earliest_pos, pos)
                
                if earliest_pos < len(response):
                    instruction_positions.append((instruction["order"], earliest_pos))
        
        if len(instruction_positions) < 2:
            return 100.0  # Can't determine order
        
        # Sort by position in response
        instruction_positions.sort(key=lambda x: x[1])
        response_order = [pos[0] for pos in instruction_positions]
        expected_order = list(range(1, len(response_order) + 1))
        
        # Calculate order correctness
        correct_positions = sum(1 for i in range(len(response_order)) if response_order[i] == expected_order[i])
        
        return (correct_positions / len(response_order)) * 100.0
    
    def _check_constraints(self, criteria: Dict[str, Any], response: str) -> float:
        """Check satisfaction of specific constraints."""
        if not criteria or "constraints" not in criteria:
            return 100.0
        
        constraints = criteria["constraints"]
        satisfied_constraints = 0
        total_constraints = len(constraints)
        
        for constraint in constraints:
            constraint_type = constraint.get("type", "")
            
            if constraint_type == "include_keywords":
                keywords = constraint.get("keywords", [])
                found_keywords = sum(1 for keyword in keywords if keyword.lower() in response.lower())
                
                if found_keywords == len(keywords):
                    satisfied_constraints += 1
                elif found_keywords >= len(keywords) * 0.7:
                    satisfied_constraints += 0.7
            
            elif constraint_type == "exclude_keywords":
                keywords = constraint.get("keywords", [])
                found_keywords = sum(1 for keyword in keywords if keyword.lower() in response.lower())
                
                if found_keywords == 0:
                    satisfied_constraints += 1
            
            elif constraint_type == "max_length":
                max_words = constraint.get("max_words", float('inf'))
                actual_words = len(response.split())
                
                if actual_words <= max_words:
                    satisfied_constraints += 1
                else:
                    # Partial credit for being close
                    excess_ratio = (actual_words - max_words) / max_words
                    satisfied_constraints += max(0, 1 - excess_ratio)
            
            elif constraint_type == "min_length":
                min_words = constraint.get("min_words", 0)
                actual_words = len(response.split())
                
                if actual_words >= min_words:
                    satisfied_constraints += 1
                else:
                    # Partial credit based on how close
                    satisfied_constraints += actual_words / min_words
        
        return (satisfied_constraints / total_constraints) * 100.0 if total_constraints > 0 else 100.0
    
    def _check_detail_level(self, criteria: Dict[str, Any], response: str) -> float:
        """Check if the response has appropriate level of detail."""
        if not criteria or "detail_level" not in criteria:
            return 100.0
        
        expected_level = criteria["detail_level"].lower()
        response_length = len(response.split())
        
        # Analyze response characteristics
        has_examples = bool(re.search(r'\b(?:for example|such as|e\.g\.|like|including)\b', response, re.IGNORECASE))
        has_explanations = bool(re.search(r'\b(?:because|since|due to|reason|explanation)\b', response, re.IGNORECASE))
        has_specifics = len(re.findall(r'\b\d+\b', response)) > 0
        
        if expected_level == "brief":
            # Brief responses should be concise
            if response_length <= 100:
                return 100.0
            elif response_length <= 200:
                return 70.0
            else:
                return 40.0
        
        elif expected_level == "detailed":
            # Detailed responses should have examples, explanations, specifics
            score = 0.0
            
            if response_length >= 200:
                score += 30
            elif response_length >= 100:
                score += 20
            else:
                score += 10
            
            if has_examples:
                score += 25
            if has_explanations:
                score += 25
            if has_specifics:
                score += 20
            
            return min(100.0, score)
        
        elif expected_level == "comprehensive":
            # Comprehensive responses need all elements
            score = 0.0
            
            if response_length >= 400:
                score += 40
            elif response_length >= 200:
                score += 25
            else:
                score += 10
            
            if has_examples:
                score += 20
            if has_explanations:
                score += 20
            if has_specifics:
                score += 20
            
            return min(100.0, score)
        
        return 100.0
    
    def _analyze_instructions(self, prompt: str) -> Dict[str, Any]:
        """Analyze the complexity and characteristics of instructions."""
        instructions = self._parse_instructions(prompt)
        
        return {
            "total_instructions": len(instructions),
            "instruction_types": list(set(inst.get("type", "unknown") for inst in instructions)),
            "has_ordering": any("order" in inst for inst in instructions),
            "complexity_score": min(100, len(instructions) * 20 + len(prompt.split()) // 10)
        }
    
    def _analyze_response(self, response: str) -> Dict[str, Any]:
        """Analyze response characteristics."""
        return {
            "word_count": len(response.split()),
            "sentence_count": len(re.split(r'[.!?]+', response)),
            "paragraph_count": len(response.split('\n\n')),
            "has_structure": bool(re.search(r'(?:\d+\.|\b(?:first|second|third|finally)\b|[•\-\*])', response, re.IGNORECASE)),
            "has_examples": bool(re.search(r'\b(?:for example|such as|e\.g\.)\b', response, re.IGNORECASE))
        }
    
    def get_evaluation_criteria(self) -> Dict[str, Any]:
        """Get evaluation criteria for instruction following."""
        return {
            "name": "Instruction Following",
            "description": "Evaluates how well the model follows complex, multi-step instructions",
            "scoring_components": {
                "completeness": "Addresses all parts of instructions (30%)",
                "format_compliance": "Follows format requirements (25%)",
                "order_adherence": "Follows correct order (20%)",
                "constraint_satisfaction": "Satisfies specific constraints (15%)",
                "detail_level": "Appropriate level of detail (10%)"
            },
            "passing_threshold": 70.0,
            "max_score": 100.0
        }