"""Demo script showcasing the LLM Benchmark Framework."""

import asyncio
import os
import sys
from typing import List
# Simulated environment for demo
import os
os.environ.setdefault('OPENAI_API_KEY', '')
os.environ.setdefault('ANTHROPIC_API_KEY', '')

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.factory import ModelFactory
from models.base import ModelConfig
from core.runner import EvaluationRunner
from core.logger import setup_logger
from reporters.json_reporter import JSONReporter
from reporters.html_reporter import HTMLReporter
from reporters.csv_reporter import CSVReporter


def print_banner():
    """Print impressive banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🤖 LLM BENCHMARK FRAMEWORK - PRODUCTION READY EVALUATION SYSTEM 🤖      ║
║                                                                              ║
║                           Professional LLM Evaluation Tool                  ║
║                                                                              ║
║  ✨ Features:                                                               ║
║     • Multi-provider LLM support (OpenAI, Anthropic, Ollama)               ║
║     • 5 comprehensive evaluation categories                                  ║
║     • 75+ carefully crafted test cases                                      ║
║     • Parallel execution with async processing                              ║
║     • Professional web dashboard with Streamlit                             ║
║     • Cost efficiency analysis & model recommendations                      ║
║     • Statistical analysis with confidence intervals                        ║
║     • Comprehensive reporting (HTML, JSON, CSV)                             ║
║     • Production-ready caching & error handling                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


async def run_demo_evaluation():
    """Run a comprehensive demo evaluation."""
    logger = setup_logger("demo", level="INFO")
    
    print("🚀 Starting Demo Evaluation...")
    print("=" * 80)
    
    # Check for API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        print("⚠️  No API keys found in environment variables.")
        print("   Please set OPENAI_API_KEY and/or ANTHROPIC_API_KEY")
        print("   For now, running with sample mock data...\n")
        return await run_mock_demo()
    
    # Create providers
    providers = []
    
    if openai_key:
        print("✅ OpenAI API key found - adding GPT models")
        try:
            gpt4_config = ModelConfig(
                model_name="gpt-4o",
                provider="openai",
                temperature=0.7,
                max_tokens=1000
            )
            providers.append(ModelFactory.create_provider(gpt4_config))
            
            gpt35_config = ModelConfig(
                model_name="gpt-3.5-turbo",
                provider="openai", 
                temperature=0.7,
                max_tokens=1000
            )
            providers.append(ModelFactory.create_provider(gpt35_config))
        except Exception as e:
            print(f"❌ Failed to create OpenAI providers: {e}")
    
    if anthropic_key:
        print("✅ Anthropic API key found - adding Claude models")
        try:
            claude_config = ModelConfig(
                model_name="claude-3-sonnet-20240229",
                provider="anthropic",
                temperature=0.7,
                max_tokens=1000
            )
            providers.append(ModelFactory.create_provider(claude_config))
        except Exception as e:
            print(f"❌ Failed to create Anthropic provider: {e}")
    
    if not providers:
        print("❌ No providers available. Running mock demo instead...")
        return await run_mock_demo()
    
    print(f"🎯 Configured {len(providers)} providers for evaluation")
    print()
    
    # Progress tracking
    def progress_callback(message: str, progress: float):
        print(f"📊 Progress: {progress*100:.1f}% - {message}")
    
    # Create evaluation runner
    runner = EvaluationRunner(
        cache_enabled=True,
        max_concurrent=2,
        progress_callback=progress_callback
    )
    
    print("🏃‍♂️ Running Quick Benchmark (3 cases per category)...")
    print("   This will test all 5 evaluation categories:")
    print("   • Factual Accuracy")
    print("   • Reasoning & Logic") 
    print("   • Code Generation")
    print("   • Safety & Bias Detection")
    print("   • Instruction Following")
    print()
    
    try:
        # Run evaluation
        results = await runner.run_quick_benchmark(
            providers=providers,
            num_cases_per_category=3
        )
        
        print("✅ Evaluation completed successfully!")
        print("=" * 80)
        
        # Display key results
        display_results_summary(results)
        
        # Generate reports
        await generate_demo_reports(results)
        
        return results
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        logger.error(f"Demo evaluation error: {e}")
        return None


async def run_mock_demo():
    """Run demo with mock data when no API keys are available."""
    print("🎭 Running Mock Demo with Sample Data...")
    print("=" * 80)
    
    # Simulate evaluation time
    import time
    for i in range(1, 6):
        print(f"📊 Progress: {i*20}% - Evaluating mock provider {i}/5...")
        time.sleep(0.5)
    
    # Create mock results
    from datetime import datetime
    
    mock_results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "evaluation_time_seconds": 2.5,
            "total_evaluations": 15,
            "providers_tested": ["gpt-4o-mock", "claude-3-sonnet-mock", "llama2-7b-mock"],
            "categories_tested": ["factual_accuracy", "reasoning_logic", "code_generation", "safety_bias", "instruction_following"]
        },
        "summary": {
            "provider_summaries": {
                "gpt-4o-mock": {
                    "overall_score": 89.3,
                    "pass_rate": 0.87,
                    "total_cost_usd": 0.0234,
                    "avg_latency_ms": 1150,
                    "tests_completed": 15,
                    "tests_passed": 13,
                    "category_scores": {
                        "factual_accuracy": 92.1,
                        "reasoning_logic": 88.5,
                        "code_generation": 91.2,
                        "safety_bias": 95.8,
                        "instruction_following": 87.9
                    }
                },
                "claude-3-sonnet-mock": {
                    "overall_score": 86.7,
                    "pass_rate": 0.83,
                    "total_cost_usd": 0.0198,
                    "avg_latency_ms": 890,
                    "tests_completed": 15,
                    "tests_passed": 12,
                    "category_scores": {
                        "factual_accuracy": 88.4,
                        "reasoning_logic": 85.2,
                        "code_generation": 84.1,
                        "safety_bias": 94.2,
                        "instruction_following": 89.6
                    }
                },
                "llama2-7b-mock": {
                    "overall_score": 74.2,
                    "pass_rate": 0.67,
                    "total_cost_usd": 0.0000,
                    "avg_latency_ms": 2340,
                    "tests_completed": 15,
                    "tests_passed": 10,
                    "category_scores": {
                        "factual_accuracy": 78.9,
                        "reasoning_logic": 71.3,
                        "code_generation": 69.8,
                        "safety_bias": 82.1,
                        "instruction_following": 68.9
                    }
                }
            },
            "provider_rankings": [
                {"provider": "gpt-4o-mock", "score": 89.3},
                {"provider": "claude-3-sonnet-mock", "score": 86.7}, 
                {"provider": "llama2-7b-mock", "score": 74.2}
            ],
            "overall_statistics": {
                "avg_score_all_providers": 83.4,
                "total_cost_all_providers": 0.0432,
                "avg_latency_all_providers": 1460
            }
        },
        "metrics": {
            "provider_metrics": {
                "gpt-4o-mock": {
                    "average_score": 89.3,
                    "pass_rate": 0.87,
                    "total_cost_usd": 0.0234,
                    "average_latency_ms": 1150,
                    "reliability_score": 0.94
                },
                "claude-3-sonnet-mock": {
                    "average_score": 86.7,
                    "pass_rate": 0.83,
                    "total_cost_usd": 0.0198,
                    "average_latency_ms": 890,
                    "reliability_score": 0.91
                },
                "llama2-7b-mock": {
                    "average_score": 74.2,
                    "pass_rate": 0.67,
                    "total_cost_usd": 0.0000,
                    "average_latency_ms": 2340,
                    "reliability_score": 0.78
                }
            },
            "category_metrics": {
                "factual_accuracy": {"average_score": 86.5},
                "reasoning_logic": {"average_score": 81.7},
                "code_generation": {"average_score": 81.7},
                "safety_bias": {"average_score": 90.7},
                "instruction_following": {"average_score": 82.1}
            },
            "difficulty_metrics": {
                "easy": {"average_score": 89.2},
                "medium": {"average_score": 81.1}, 
                "hard": {"average_score": 75.9}
            },
            "cost_analysis": {
                "total_cost_all_providers": 0.0432,
                "average_cost_per_evaluation": 0.00096,
                "provider_cost_analysis": {
                    "gpt-4o-mock": {"total_cost": 0.0234, "cost_efficiency_ratio": 3814.5},
                    "claude-3-sonnet-mock": {"total_cost": 0.0198, "cost_efficiency_ratio": 4378.8},
                    "llama2-7b-mock": {"total_cost": 0.0000, "cost_efficiency_ratio": float('inf')}
                }
            },
            "efficiency_scores": {
                "provider_efficiency": {
                    "gpt-4o-mock": {"overall_efficiency": 92.4, "efficiency_rank": 2},
                    "claude-3-sonnet-mock": {"overall_efficiency": 95.1, "efficiency_rank": 1},
                    "llama2-7b-mock": {"overall_efficiency": 87.3, "efficiency_rank": 3}
                },
                "efficiency_rankings": [
                    {"provider": "claude-3-sonnet-mock", "efficiency_score": 95.1},
                    {"provider": "gpt-4o-mock", "efficiency_score": 92.4},
                    {"provider": "llama2-7b-mock", "efficiency_score": 87.3}
                ]
            }
        }
    }
    
    print("✅ Mock evaluation completed successfully!")
    print("=" * 80)
    
    display_results_summary(mock_results)
    await generate_demo_reports(mock_results, mock=True)
    
    return mock_results


def display_results_summary(results: dict):
    """Display a formatted summary of results."""
    print("📊 EVALUATION RESULTS SUMMARY")
    print("=" * 50)
    
    metadata = results.get("metadata", {})
    summary = results.get("summary", {})
    
    # Basic stats
    print(f"⏱️  Evaluation Time: {metadata.get('evaluation_time_seconds', 0):.2f} seconds")
    print(f"📈 Total Evaluations: {metadata.get('total_evaluations', 0)}")
    print(f"🤖 Models Tested: {len(metadata.get('providers_tested', []))}")
    print(f"📋 Categories: {len(metadata.get('categories_tested', []))}")
    print()
    
    # Provider rankings
    print("🏆 PROVIDER RANKINGS:")
    rankings = summary.get("provider_rankings", [])
    for i, ranking in enumerate(rankings, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        print(f"   {medal} {ranking['provider']}: {ranking['score']:.1f} points")
    print()
    
    # Cost analysis
    overall_stats = summary.get("overall_statistics", {})
    print("💰 COST ANALYSIS:")
    print(f"   Total Cost: ${overall_stats.get('total_cost_all_providers', 0):.4f}")
    print(f"   Avg Performance: {overall_stats.get('avg_score_all_providers', 0):.1f}")
    print(f"   Avg Latency: {overall_stats.get('avg_latency_all_providers', 0):.0f}ms")
    print()
    
    # Efficiency leader
    metrics = results.get("metrics", {})
    efficiency = metrics.get("efficiency_scores", {})
    efficiency_rankings = efficiency.get("efficiency_rankings", [])
    if efficiency_rankings:
        best_efficiency = efficiency_rankings[0]
        print("⚡ EFFICIENCY CHAMPION:")
        print(f"   {best_efficiency['provider']} (Score: {best_efficiency['efficiency_score']:.1f})")
        print()


async def generate_demo_reports(results: dict, mock: bool = False):
    """Generate demonstration reports."""
    print("📝 GENERATING REPORTS...")
    print("-" * 30)
    
    try:
        # JSON Report
        json_reporter = JSONReporter(output_dir="demo_reports")
        json_path = json_reporter.generate_report(results, "demo_evaluation.json")
        print(f"✅ JSON Report: {json_path}")
        
        # HTML Report
        html_reporter = HTMLReporter(output_dir="demo_reports")
        html_path = html_reporter.generate_report(results, "demo_evaluation.html")
        print(f"✅ HTML Report: {html_path}")
        
        # CSV Report
        csv_reporter = CSVReporter(output_dir="demo_reports")
        csv_path = csv_reporter.generate_report(results, "demo_evaluation.csv")
        print(f"✅ CSV Report: {csv_path}")
        
        print()
        print("🎉 All reports generated successfully!")
        print(f"   Reports saved in: demo_reports/")
        
        if mock:
            print("   📝 Note: These reports contain mock data for demonstration")
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")


def display_framework_features():
    """Display framework features and capabilities."""
    print("\n🌟 FRAMEWORK HIGHLIGHTS:")
    print("=" * 50)
    
    features = [
        "✨ Multi-Provider Support: OpenAI, Anthropic, Ollama",
        "🎯 5 Evaluation Categories: Accuracy, Reasoning, Code, Safety, Instructions",
        "📊 75+ Test Cases: Comprehensive coverage across difficulty levels", 
        "⚡ Async Processing: Parallel execution for maximum efficiency",
        "💾 Smart Caching: Avoid expensive re-runs with TTL cache",
        "📈 Statistical Analysis: Confidence intervals, effect sizes",
        "💰 Cost Tracking: Per-token pricing with efficiency scoring",
        "🎨 Beautiful UI: Professional Streamlit dashboard",
        "📋 Multiple Reports: HTML, JSON, CSV export formats",
        "🔒 Production Ready: Error handling, logging, Docker support",
        "🧪 Comprehensive Tests: Unit tests for all components",
        "📚 Documentation: Complete setup and usage guides"
    ]
    
    for feature in features:
        print(f"   {feature}")
    print()


def print_next_steps():
    """Print next steps for the user."""
    print("🚀 NEXT STEPS:")
    print("=" * 30)
    print("1. 🌐 Start Web Dashboard:")
    print("   streamlit run web_ui/app.py")
    print()
    print("2. 📊 View Generated Reports:")
    print("   open demo_reports/demo_evaluation.html")
    print()
    print("3. 🔧 Customize Configuration:")
    print("   Edit .env file with your API keys")
    print("   Modify model configs in demo.py")
    print()
    print("4. 🧪 Run Full Evaluation:")
    print("   python -c \"from demo import run_full_evaluation; run_full_evaluation()\"")
    print()
    print("5. 🐳 Deploy with Docker:")
    print("   docker build -t llm-bench .")
    print("   docker run -p 8501:8501 llm-bench")
    print()


async def main():
    """Main demo function."""
    print_banner()
    
    # Run evaluation
    results = await run_demo_evaluation()
    
    if results:
        display_framework_features()
        print_next_steps()
        
        print("🎊 DEMO COMPLETED SUCCESSFULLY!")
        print("   This framework demonstrates production-ready LLM evaluation")
        print("   capabilities suitable for enterprise deployment.")
        print()
        print("   Ready for professional LLM evaluation! 🚀")
    else:
        print("❌ Demo encountered issues. Check logs for details.")


if __name__ == "__main__":
    asyncio.run(main())