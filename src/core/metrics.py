"""Comprehensive metrics calculation and analysis."""

import statistics
from typing import List, Dict, Any, Optional
from collections import defaultdict
import math

from evaluators.base import EvaluationResult


class MetricsCalculator:
    """Calculates comprehensive metrics from evaluation results."""
    
    @staticmethod
    def calculate_comprehensive_metrics(results: List[EvaluationResult]) -> Dict[str, Any]:
        """Calculate comprehensive metrics from evaluation results."""
        if not results:
            return {"error": "No results provided"}
        
        metrics = {
            "overall_metrics": MetricsCalculator._calculate_overall_metrics(results),
            "provider_metrics": MetricsCalculator._calculate_provider_metrics(results),
            "category_metrics": MetricsCalculator._calculate_category_metrics(results),
            "difficulty_metrics": MetricsCalculator._calculate_difficulty_metrics(results),
            "cost_analysis": MetricsCalculator._calculate_cost_analysis(results),
            "performance_analysis": MetricsCalculator._calculate_performance_analysis(results),
            "statistical_analysis": MetricsCalculator._calculate_statistical_analysis(results),
            "efficiency_scores": MetricsCalculator._calculate_efficiency_scores(results)
        }
        
        return metrics
    
    @staticmethod
    def _calculate_overall_metrics(results: List[EvaluationResult]) -> Dict[str, Any]:
        """Calculate overall performance metrics."""
        scores = [r.score for r in results]
        pass_rate = sum(1 for r in results if r.passed) / len(results)
        
        return {
            "total_evaluations": len(results),
            "average_score": statistics.mean(scores),
            "median_score": statistics.median(scores),
            "min_score": min(scores),
            "max_score": max(scores),  
            "score_std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
            "pass_rate": pass_rate,
            "total_passed": sum(1 for r in results if r.passed),
            "total_failed": sum(1 for r in results if not r.passed)
        }
    
    @staticmethod
    def _calculate_provider_metrics(results: List[EvaluationResult]) -> Dict[str, Any]:
        """Calculate metrics grouped by provider."""
        provider_results = defaultdict(list)
        for result in results:
            provider_results[result.provider].append(result)
        
        provider_metrics = {}
        for provider, provider_results_list in provider_results.items():
            scores = [r.score for r in provider_results_list]
            latencies = [r.response.latency_ms for r in provider_results_list]
            costs = [r.response.cost_usd for r in provider_results_list]
            
            # Category breakdown
            category_scores = defaultdict(list)
            for result in provider_results_list:
                category_scores[result.category].append(result.score)
            
            category_averages = {
                cat: statistics.mean(scores) for cat, scores in category_scores.items()
            }
            
            # Difficulty breakdown
            difficulty_scores = defaultdict(list)
            for result in provider_results_list:
                difficulty_scores[result.difficulty].append(result.score)
            
            difficulty_averages = {
                diff: statistics.mean(scores) for diff, scores in difficulty_scores.items()
            }
            
            provider_metrics[provider] = {
                "total_evaluations": len(provider_results_list),
                "average_score": statistics.mean(scores),
                "median_score": statistics.median(scores),
                "score_std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
                "pass_rate": sum(1 for r in provider_results_list if r.passed) / len(provider_results_list),
                "average_latency_ms": statistics.mean(latencies),
                "total_cost_usd": sum(costs),
                "average_cost_per_request": statistics.mean(costs),
                "category_scores": category_averages,
                "difficulty_scores": difficulty_averages,
                "reliability_score": MetricsCalculator._calculate_reliability_score(provider_results_list)
            }
        
        return provider_metrics
    
    @staticmethod
    def _calculate_category_metrics(results: List[EvaluationResult]) -> Dict[str, Any]:
        """Calculate metrics grouped by category."""
        category_results = defaultdict(list)
        for result in results:
            category_results[result.category].append(result)
        
        category_metrics = {}
        for category, category_results_list in category_results.items():
            scores = [r.score for r in category_results_list]
            
            # Provider performance in this category
            provider_scores = defaultdict(list)
            for result in category_results_list:
                provider_scores[result.provider].append(result.score)
            
            provider_averages = {
                provider: statistics.mean(scores) for provider, scores in provider_scores.items()
            }
            
            category_metrics[category] = {
                "total_evaluations": len(category_results_list),
                "average_score": statistics.mean(scores),
                "median_score": statistics.median(scores),
                "score_std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
                "pass_rate": sum(1 for r in category_results_list if r.passed) / len(category_results_list),
                "provider_performance": provider_averages,
                "difficulty_distribution": MetricsCalculator._get_difficulty_distribution(category_results_list)
            }
        
        return category_metrics
    
    @staticmethod
    def _calculate_difficulty_metrics(results: List[EvaluationResult]) -> Dict[str, Any]:
        """Calculate metrics grouped by difficulty."""
        difficulty_results = defaultdict(list)
        for result in results:
            difficulty_results[result.difficulty].append(result)
        
        difficulty_metrics = {}
        for difficulty, difficulty_results_list in difficulty_results.items():
            scores = [r.score for r in difficulty_results_list]
            
            difficulty_metrics[difficulty] = {
                "total_evaluations": len(difficulty_results_list),
                "average_score": statistics.mean(scores),
                "median_score": statistics.median(scores),
                "pass_rate": sum(1 for r in difficulty_results_list if r.passed) / len(difficulty_results_list),
                "score_range": max(scores) - min(scores)
            }
        
        return difficulty_metrics
    
    @staticmethod
    def _calculate_cost_analysis(results: List[EvaluationResult]) -> Dict[str, Any]:
        """Calculate cost-related metrics."""
        costs = [r.response.cost_usd for r in results]
        total_cost = sum(costs)
        
        # Cost by provider
        provider_costs = defaultdict(list)
        for result in results:
            provider_costs[result.provider].append(result.response.cost_usd)
        
        provider_cost_analysis = {}
        for provider, provider_costs_list in provider_costs.items():
            provider_cost_analysis[provider] = {
                "total_cost": sum(provider_costs_list),
                "average_cost_per_request": statistics.mean(provider_costs_list),
                "cost_efficiency_ratio": MetricsCalculator._calculate_cost_efficiency_ratio(
                    results, provider
                )
            }
        
        return {
            "total_cost_all_providers": total_cost,
            "average_cost_per_evaluation": statistics.mean(costs) if costs else 0,
            "cost_distribution": {
                "min_cost": min(costs) if costs else 0,
                "max_cost": max(costs) if costs else 0,
                "median_cost": statistics.median(costs) if costs else 0
            },
            "provider_cost_analysis": provider_cost_analysis
        }
    
    @staticmethod
    def _calculate_performance_analysis(results: List[EvaluationResult]) -> Dict[str, Any]:
        """Calculate performance-related metrics."""
        latencies = [r.response.latency_ms for r in results]
        
        token_counts = [r.response.total_tokens for r in results]
        
        # Performance by provider
        provider_performance = defaultdict(list)
        for result in results:
            provider_performance[result.provider].append({
                "latency": result.response.latency_ms,
                "tokens": result.response.total_tokens,
                "score": result.score
            })
        
        provider_perf_analysis = {}
        for provider, perf_data in provider_performance.items():
            latencies_p = [p["latency"] for p in perf_data]
            tokens_p = [p["tokens"] for p in perf_data]
            scores_p = [p["score"] for p in perf_data]
            
            provider_perf_analysis[provider] = {
                "average_latency_ms": statistics.mean(latencies_p),
                "latency_std_dev": statistics.stdev(latencies_p) if len(latencies_p) > 1 else 0,
                "average_tokens_per_response": statistics.mean(tokens_p),
                "tokens_per_second": statistics.mean([
                    t / (l / 1000) if l > 0 else 0 for t, l in zip(tokens_p, latencies_p)
                ]),
                "performance_consistency": 1 / (statistics.stdev(scores_p) + 1) if len(scores_p) > 1 else 1
            }
        
        return {
            "overall_latency": {
                "average_ms": statistics.mean(latencies),
                "median_ms": statistics.median(latencies),
                "min_ms": min(latencies),
                "max_ms": max(latencies),
                "std_dev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0
            },
            "token_statistics": {
                "average_tokens_per_response": statistics.mean(token_counts),
                "total_tokens_processed": sum(token_counts)
            },
            "provider_performance": provider_perf_analysis
        }
    
    @staticmethod
    def _calculate_statistical_analysis(results: List[EvaluationResult]) -> Dict[str, Any]:
        """Calculate statistical significance and confidence intervals."""
        if len(results) < 2:
            return {"error": "Insufficient data for statistical analysis"}
        
        scores = [r.score for r in results]
        n = len(scores)
        mean_score = statistics.mean(scores)
        std_dev = statistics.stdev(scores)
        
        # 95% confidence interval
        confidence_interval = MetricsCalculator._calculate_confidence_interval(scores, 0.95)
        
        # Provider comparison (if multiple providers)
        provider_scores = defaultdict(list)
        for result in results:
            provider_scores[result.provider].append(result.score)
        
        provider_comparisons = {}
        if len(provider_scores) > 1:
            providers = list(provider_scores.keys())
            for i, provider1 in enumerate(providers):
                for provider2 in providers[i+1:]:
                    comparison_key = f"{provider1}_vs_{provider2}"
                    
                    scores1 = provider_scores[provider1]
                    scores2 = provider_scores[provider2]
                    
                    # Effect size (Cohen's d)
                    effect_size = MetricsCalculator._calculate_cohens_d(scores1, scores2)
                    
                    provider_comparisons[comparison_key] = {
                        "mean_difference": statistics.mean(scores1) - statistics.mean(scores2),
                        "effect_size": effect_size,
                        "effect_size_interpretation": MetricsCalculator._interpret_effect_size(effect_size)
                    }
        
        return {
            "sample_size": n,
            "confidence_interval_95": confidence_interval,
            "coefficient_of_variation": (std_dev / mean_score) * 100 if mean_score > 0 else 0,
            "provider_comparisons": provider_comparisons,
            "score_distribution": {
                "skewness": MetricsCalculator._calculate_skewness(scores),
                "kurtosis": MetricsCalculator._calculate_kurtosis(scores)
            }
        }
    
    @staticmethod
    def _calculate_efficiency_scores(results: List[EvaluationResult]) -> Dict[str, Any]:
        """Calculate efficiency scores combining performance and cost."""
        provider_efficiency = {}
        
        provider_results = defaultdict(list)
        for result in results:
            provider_results[result.provider].append(result)
        
        for provider, provider_results_list in provider_results.items():
            scores = [r.score for r in provider_results_list]
            costs = [r.response.cost_usd for r in provider_results_list]
            latencies = [r.response.latency_ms for r in provider_results_list]
            
            avg_score = statistics.mean(scores)
            avg_cost = statistics.mean(costs)
            avg_latency = statistics.mean(latencies)
            
            # Cost efficiency: score per dollar
            cost_efficiency = avg_score / avg_cost if avg_cost > 0 else 0
            
            # Speed efficiency: score per second
            speed_efficiency = avg_score / (avg_latency / 1000) if avg_latency > 0 else 0
            
            # Overall efficiency: weighted combination
            overall_efficiency = (cost_efficiency * 0.6) + (speed_efficiency * 0.4)
            
            provider_efficiency[provider] = {
                "cost_efficiency": cost_efficiency,
                "speed_efficiency": speed_efficiency,
                "overall_efficiency": overall_efficiency,
                "efficiency_rank": 0  # Will be set after all providers are processed
            }
        
        # Rank providers by overall efficiency
        ranked_providers = sorted(
            provider_efficiency.items(),
            key=lambda x: x[1]["overall_efficiency"],
            reverse=True
        )
        
        for rank, (provider, metrics) in enumerate(ranked_providers, 1):
            provider_efficiency[provider]["efficiency_rank"] = rank
        
        return {
            "provider_efficiency": provider_efficiency,
            "efficiency_rankings": [
                {"provider": provider, "efficiency_score": metrics["overall_efficiency"]}
                for provider, metrics in ranked_providers
            ]
        }
    
    @staticmethod
    def _calculate_reliability_score(results: List[EvaluationResult]) -> float:
        """Calculate reliability score based on consistency and error rate."""
        if not results:
            return 0.0
        
        scores = [r.score for r in results]
        error_count = sum(1 for r in results if r.error is not None)
        
        # Consistency score (inverse of standard deviation)
        consistency = 1 / (statistics.stdev(scores) + 1) if len(scores) > 1 else 1
        
        # Error rate score
        error_rate = error_count / len(results)
        error_score = 1 - error_rate
        
        # Combined reliability score
        reliability = (consistency * 0.7) + (error_score * 0.3)
        
        return min(1.0, max(0.0, reliability))
    
    @staticmethod
    def _calculate_cost_efficiency_ratio(results: List[EvaluationResult], provider: str) -> float:
        """Calculate cost efficiency ratio for a provider."""
        provider_results = [r for r in results if r.provider == provider]
        if not provider_results:
            return 0.0
        
        total_score = sum(r.score for r in provider_results)
        total_cost = sum(r.response.cost_usd for r in provider_results)
        
        return total_score / total_cost if total_cost > 0 else 0.0
    
    @staticmethod
    def _get_difficulty_distribution(results: List[EvaluationResult]) -> Dict[str, int]:
        """Get distribution of test cases by difficulty."""
        distribution = defaultdict(int)
        for result in results:
            distribution[result.difficulty] += 1
        return dict(distribution)
    
    @staticmethod
    def _calculate_confidence_interval(values: List[float], confidence: float) -> Dict[str, float]:
        """Calculate confidence interval for a list of values."""
        n = len(values)
        if n < 2:
            return {"lower": 0.0, "upper": 0.0}
        
        mean = statistics.mean(values)
        std_err = statistics.stdev(values) / math.sqrt(n)
        
        # Using t-distribution approximation
        t_value = 1.96 if confidence == 0.95 else 2.576  # Simplified
        
        margin_error = t_value * std_err
        
        return {
            "lower": mean - margin_error,
            "upper": mean + margin_error
        }
    
    @staticmethod
    def _calculate_cohens_d(group1: List[float], group2: List[float]) -> float:
        """Calculate Cohen's d effect size."""
        if len(group1) < 2 or len(group2) < 2:
            return 0.0
        
        mean1 = statistics.mean(group1)
        mean2 = statistics.mean(group2)
        
        # Pooled standard deviation
        n1, n2 = len(group1), len(group2)
        var1 = statistics.variance(group1)
        var2 = statistics.variance(group2)
        
        pooled_std = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        return (mean1 - mean2) / pooled_std if pooled_std > 0 else 0.0
    
    @staticmethod
    def _interpret_effect_size(cohens_d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"
    
    @staticmethod
    def _calculate_skewness(values: List[float]) -> float:
        """Calculate skewness of distribution."""
        if len(values) < 3:
            return 0.0
        
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values)
        n = len(values)
        
        if std_dev == 0:
            return 0.0
        
        skewness = sum(((x - mean) / std_dev) ** 3 for x in values) / n
        return skewness
    
    @staticmethod
    def _calculate_kurtosis(values: List[float]) -> float:
        """Calculate kurtosis of distribution."""
        if len(values) < 4:
            return 0.0
        
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values)
        n = len(values)
        
        if std_dev == 0:
            return 0.0
        
        kurtosis = sum(((x - mean) / std_dev) ** 4 for x in values) / n
        return kurtosis - 3  # Excess kurtosis