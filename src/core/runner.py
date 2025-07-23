"""Core evaluation runner with parallel execution."""

import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
import logging
from dataclasses import asdict

from models.base import LLMProvider, ModelResponse
from evaluators.base import Evaluator, TestCase, EvaluationResult
from datasets.loader import DatasetLoader
from core.cache import ResultCache
from core.metrics import MetricsCalculator


class EvaluationRunner:
    """Runs evaluations across multiple models and test cases."""
    
    def __init__(
        self,
        cache_enabled: bool = True,
        max_concurrent: int = 5,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ):
        self.cache = ResultCache() if cache_enabled else None
        self.max_concurrent = max_concurrent
        self.progress_callback = progress_callback
        self.logger = logging.getLogger(__name__)
        
        # Load evaluators
        self.evaluators = self._load_evaluators()
        
    def _load_evaluators(self) -> Dict[str, Evaluator]:
        """Load all available evaluators."""
        from evaluators import (
            FactualAccuracyEvaluator,
            ReasoningLogicEvaluator,
            CodeGenerationEvaluator,
            SafetyBiasEvaluator,
            InstructionFollowingEvaluator
        )
        
        return {
            "factual_accuracy": FactualAccuracyEvaluator(),
            "reasoning_logic": ReasoningLogicEvaluator(),
            "code_generation": CodeGenerationEvaluator(),
            "safety_bias": SafetyBiasEvaluator(),
            "instruction_following": InstructionFollowingEvaluator()
        }
    
    async def run_evaluation(
        self,
        providers: List[LLMProvider],
        categories: Optional[List[str]] = None,
        difficulties: Optional[List[str]] = None,
        max_cases_per_category: Optional[int] = None
    ) -> Dict[str, Any]:
        """Run comprehensive evaluation across providers and test cases."""
        start_time = time.time()
        
        # Get test cases
        test_cases = self._get_test_cases(categories, difficulties, max_cases_per_category)
        
        self.logger.info(f"Starting evaluation with {len(providers)} providers and {len(test_cases)} test cases")
        
        # Run evaluations
        all_results = []
        total_tasks = len(providers) * len(test_cases)
        completed_tasks = 0
        
        # Create semaphore for concurrent execution
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def evaluate_single(provider: LLMProvider, test_case: TestCase) -> Optional[EvaluationResult]:
            async with semaphore:
                try:
                    result = await self._evaluate_test_case(provider, test_case)
                    nonlocal completed_tasks
                    completed_tasks += 1
                    
                    if self.progress_callback:
                        progress = completed_tasks / total_tasks
                        self.progress_callback(f"Completed {completed_tasks}/{total_tasks} evaluations", progress)
                    
                    return result
                except Exception as e:
                    self.logger.error(f"Error evaluating {provider.name} on {test_case.id}: {str(e)}")
                    return None
        
        # Create all tasks
        tasks = []
        for provider in providers:
            for test_case in test_cases:
                task = evaluate_single(provider, test_case)
                tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        all_results = [r for r in results if isinstance(r, EvaluationResult)]
        
        # Calculate metrics
        metrics = MetricsCalculator.calculate_comprehensive_metrics(all_results)
        
        # Create final report
        evaluation_time = time.time() - start_time
        
        report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "evaluation_time_seconds": evaluation_time,
                "total_test_cases": len(test_cases),
                "total_evaluations": len(all_results),
                "providers_tested": [p.name for p in providers],
                "categories_tested": list(set(tc.category for tc in test_cases)),
                "difficulties_tested": list(set(tc.difficulty for tc in test_cases))
            },
            "results": [asdict(result) for result in all_results],
            "metrics": metrics,
            "summary": self._create_summary(all_results, providers)
        }
        
        self.logger.info(f"Evaluation completed in {evaluation_time:.2f} seconds")
        return report
    
    async def _evaluate_test_case(
        self, 
        provider: LLMProvider, 
        test_case: TestCase
    ) -> EvaluationResult:
        """Evaluate a single test case with a provider."""
        # Check cache first
        if self.cache:
            cached_result = self.cache.get_result(provider.name, test_case.id)
            if cached_result:
                self.logger.debug(f"Using cached result for {provider.name} on {test_case.id}")
                return cached_result
        
        # Generate response
        try:
            response = await provider.generate(
                prompt=test_case.prompt,
                system_prompt=test_case.system_prompt
            )
        except Exception as e:
            # Create error result
            error_response = ModelResponse(
                content=f"Error: {str(e)}",
                model=provider.config.model_name,
                provider=provider.name,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                latency_ms=0.0,
                timestamp=datetime.now(),
                metadata={"error": str(e)}
            )
            response = error_response
        
        # Evaluate response
        evaluator = self.evaluators.get(test_case.category)
        if not evaluator:
            raise ValueError(f"No evaluator found for category: {test_case.category}")
        
        result = await evaluator.evaluate(test_case, response)
        
        # Cache result
        if self.cache:
            self.cache.store_result(provider.name, test_case.id, result)
        
        return result
    
    def _get_test_cases(
        self,
        categories: Optional[List[str]] = None,
        difficulties: Optional[List[str]] = None,
        max_cases_per_category: Optional[int] = None
    ) -> List[TestCase]:
        """Get filtered test cases based on criteria."""
        if categories:
            test_cases = []
            for category in categories:
                cases = DatasetLoader.get_test_cases_by_category(category)
                if max_cases_per_category:
                    cases = cases[:max_cases_per_category]
                test_cases.extend(cases)
        else:
            test_cases = DatasetLoader.get_all_test_cases()
            if max_cases_per_category:
                # Limit per category
                category_counts = {}
                filtered_cases = []
                for case in test_cases:
                    if case.category not in category_counts:
                        category_counts[case.category] = 0
                    if category_counts[case.category] < max_cases_per_category:
                        filtered_cases.append(case)
                        category_counts[case.category] += 1
                test_cases = filtered_cases
        
        # Filter by difficulty
        if difficulties:
            test_cases = [tc for tc in test_cases if tc.difficulty in difficulties]
        
        return test_cases
    
    def _create_summary(
        self, 
        results: List[EvaluationResult], 
        providers: List[LLMProvider]
    ) -> Dict[str, Any]:
        """Create evaluation summary."""
        if not results:
            return {"error": "No results to summarize"}
        
        # Group results by provider
        provider_results = {}
        for result in results:
            provider = result.provider
            if provider not in provider_results:
                provider_results[provider] = []
            provider_results[provider].append(result)
        
        # Calculate provider summaries
        provider_summaries = {}
        for provider_name, provider_results_list in provider_results.items():
            total_score = sum(r.score for r in provider_results_list)
            avg_score = total_score / len(provider_results_list)
            
            total_cost = sum(r.response.cost_usd for r in provider_results_list)
            avg_latency = sum(r.response.latency_ms for r in provider_results_list) / len(provider_results_list)
            
            passed_tests = sum(1 for r in provider_results_list if r.passed)
            pass_rate = passed_tests / len(provider_results_list)
            
            # Category breakdown
            category_scores = {}
            for result in provider_results_list:
                if result.category not in category_scores:
                    category_scores[result.category] = []
                category_scores[result.category].append(result.score)
            
            category_averages = {
                cat: sum(scores) / len(scores) 
                for cat, scores in category_scores.items()
            }
            
            provider_summaries[provider_name] = {
                "overall_score": avg_score,
                "pass_rate": pass_rate,
                "total_cost_usd": total_cost,
                "avg_latency_ms": avg_latency,
                "tests_completed": len(provider_results_list),
                "tests_passed": passed_tests,
                "category_scores": category_averages
            }
        
        # Rank providers by overall score
        ranked_providers = sorted(
            provider_summaries.items(),
            key=lambda x: x[1]["overall_score"],
            reverse=True
        )
        
        return {
            "provider_summaries": provider_summaries,
            "provider_rankings": [{"provider": name, "score": summary["overall_score"]} 
                                for name, summary in ranked_providers],
            "total_evaluations": len(results),
            "overall_statistics": {
                "avg_score_all_providers": sum(r.score for r in results) / len(results),
                "total_cost_all_providers": sum(r.response.cost_usd for r in results),
                "avg_latency_all_providers": sum(r.response.latency_ms for r in results) / len(results)
            }
        }
    
    async def run_quick_benchmark(
        self, 
        providers: List[LLMProvider], 
        num_cases_per_category: int = 3
    ) -> Dict[str, Any]:
        """Run a quick benchmark with limited test cases."""
        self.logger.info("Running quick benchmark mode")
        
        return await self.run_evaluation(
            providers=providers,
            max_cases_per_category=num_cases_per_category
        )
    
    def get_evaluation_progress(self) -> Dict[str, Any]:
        """Get current evaluation progress (if running)."""
        # This would be implemented with a progress tracking system
        # For now, return basic info
        return {
            "status": "idle",
            "message": "No evaluation currently running"
        }