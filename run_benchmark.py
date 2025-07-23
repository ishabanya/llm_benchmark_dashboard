#!/usr/bin/env python3
"""
Command-line interface for running LLM benchmarks.

This script provides a convenient CLI for running evaluations without the web interface.
Perfect for CI/CD pipelines, automated testing, and batch processing.
"""

import argparse
import asyncio
import os
import sys
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.factory import ModelFactory
from models.base import ModelConfig
from core.runner import EvaluationRunner
from core.logger import setup_logger
from datasets.loader import DatasetLoader
from reporters.json_reporter import JSONReporter
from reporters.html_reporter import HTMLReporter
from reporters.csv_reporter import CSVReporter


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="LLM Benchmark Framework - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick benchmark with default models
  python run_benchmark.py --quick

  # Full benchmark with specific models
  python run_benchmark.py --models gpt-4o claude-3-sonnet --categories factual_accuracy reasoning_logic

  # Custom configuration
  python run_benchmark.py --models gpt-3.5-turbo --max-cases 5 --output-dir custom_reports

  # Generate only specific report formats
  python run_benchmark.py --quick --reports json csv
        """
    )

    # Model selection
    parser.add_argument(
        '--models',
        nargs='+',
        default=['gpt-4o', 'claude-3-sonnet'],
        help='Models to evaluate (default: gpt-4o claude-3-sonnet)'
    )

    # Evaluation configuration
    parser.add_argument(
        '--categories',
        nargs='+',
        choices=DatasetLoader.get_available_categories(),
        default=DatasetLoader.get_available_categories(),
        help='Evaluation categories to include'
    )

    parser.add_argument(
        '--difficulties',
        nargs='+',
        choices=['easy', 'medium', 'hard'],
        default=['easy', 'medium', 'hard'],
        help='Difficulty levels to include'
    )

    parser.add_argument(
        '--max-cases',
        type=int,
        default=10,
        help='Maximum test cases per category (default: 10)'
    )

    # Execution options
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick benchmark (3 cases per category)'
    )

    parser.add_argument(
        '--concurrent',
        type=int,
        default=3,
        help='Maximum concurrent evaluations (default: 3)'
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable result caching'
    )

    # Output options
    parser.add_argument(
        '--output-dir',
        default='reports',
        help='Output directory for reports (default: reports)'
    )

    parser.add_argument(
        '--reports',
        nargs='+',
        choices=['json', 'html', 'csv'],
        default=['json', 'html', 'csv'],
        help='Report formats to generate'
    )

    parser.add_argument(
        '--filename',
        help='Custom filename prefix for reports'
    )

    # Logging
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    # Dry run
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show configuration without running evaluation'
    )

    return parser.parse_args()


def create_providers(model_names: List[str], logger) -> List:
    """Create LLM providers from model names."""
    providers = []
    
    for model_name in model_names:
        try:
            # Determine provider type
            if model_name.startswith('gpt'):
                provider_name = 'openai'
            elif model_name.startswith('claude'):
                provider_name = 'anthropic'
            elif 'llama' in model_name.lower():
                provider_name = 'ollama'
            else:
                logger.warning(f"Unknown model type for {model_name}, skipping")
                continue
            
            # Create configuration
            config = ModelConfig(
                model_name=model_name,
                provider=provider_name,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Create provider
            provider = ModelFactory.create_provider(config)
            providers.append(provider)
            logger.info(f"✅ Created provider for {model_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create provider for {model_name}: {e}")
            continue
    
    return providers


def print_configuration(args, providers, logger):
    """Print evaluation configuration."""
    print("🤖 LLM Benchmark Configuration")
    print("=" * 50)
    print(f"Models: {[p.config.model_name for p in providers]}")
    print(f"Categories: {args.categories}")
    print(f"Difficulties: {args.difficulties}")
    print(f"Max cases per category: {args.max_cases if not args.quick else 3}")
    print(f"Concurrent evaluations: {args.concurrent}")
    print(f"Cache enabled: {not args.no_cache}")
    print(f"Output directory: {args.output_dir}")
    print(f"Report formats: {args.reports}")
    print()


async def run_evaluation(args, providers, logger):
    """Run the evaluation with given configuration."""
    # Progress tracking
    def progress_callback(message: str, progress: float):
        if args.verbose:
            print(f"📊 Progress: {progress*100:.1f}% - {message}")
    
    # Create evaluation runner
    runner = EvaluationRunner(
        cache_enabled=not args.no_cache,
        max_concurrent=args.concurrent,
        progress_callback=progress_callback if args.verbose else None
    )
    
    logger.info("🚀 Starting evaluation...")
    
    try:
        if args.quick:
            results = await runner.run_quick_benchmark(
                providers=providers,
                num_cases_per_category=3
            )
        else:
            results = await runner.run_evaluation(
                providers=providers,
                categories=args.categories,
                difficulties=args.difficulties,
                max_cases_per_category=args.max_cases
            )
        
        logger.info("✅ Evaluation completed successfully!")
        return results
        
    except Exception as e:
        logger.error(f"❌ Evaluation failed: {e}")
        raise


def generate_reports(results: dict, args, logger):
    """Generate reports in specified formats."""
    logger.info("📝 Generating reports...")
    
    generated_files = []
    
    try:
        # Determine filename
        if args.filename:
            base_filename = args.filename
        else:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"benchmark_report_{timestamp}"
        
        # Generate requested report formats
        if 'json' in args.reports:
            reporter = JSONReporter(output_dir=args.output_dir)
            filepath = reporter.generate_report(results, f"{base_filename}.json")
            generated_files.append(filepath)
            logger.info(f"✅ JSON report: {filepath}")
        
        if 'html' in args.reports:
            reporter = HTMLReporter(output_dir=args.output_dir)
            filepath = reporter.generate_report(results, f"{base_filename}.html")
            generated_files.append(filepath)
            logger.info(f"✅ HTML report: {filepath}")
        
        if 'csv' in args.reports:
            reporter = CSVReporter(output_dir=args.output_dir)
            filepath = reporter.generate_report(results, f"{base_filename}.csv")
            generated_files.append(filepath)
            logger.info(f"✅ CSV report: {filepath}")
        
        return generated_files
        
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        return []


def print_results_summary(results: dict):
    """Print a brief summary of results."""
    print("\n📊 EVALUATION RESULTS SUMMARY")
    print("=" * 50)
    
    metadata = results.get("metadata", {})
    summary = results.get("summary", {})
    
    # Basic stats
    print(f"⏱️  Duration: {metadata.get('evaluation_time_seconds', 0):.2f} seconds")
    print(f"📈 Total Evaluations: {metadata.get('total_evaluations', 0)}")
    print(f"🤖 Models Tested: {len(metadata.get('providers_tested', []))}")
    
    # Top performer
    rankings = summary.get("provider_rankings", [])
    if rankings:
        best = rankings[0]
        print(f"🏆 Top Performer: {best['provider']} ({best['score']:.1f} points)")
    
    # Cost summary
    overall_stats = summary.get("overall_statistics", {})
    total_cost = overall_stats.get("total_cost_all_providers", 0)
    avg_score = overall_stats.get("avg_score_all_providers", 0)
    print(f"💰 Total Cost: ${total_cost:.4f}")
    print(f"📊 Average Score: {avg_score:.1f}")
    print()


async def main():
    """Main CLI function."""
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logger(
        name="cli_benchmark",
        level=args.log_level,
        console_output=True
    )
    
    # Check for API keys
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
        logger.error("❌ No API keys found. Please set OPENAI_API_KEY and/or ANTHROPIC_API_KEY")
        sys.exit(1)
    
    # Create providers
    providers = create_providers(args.models, logger)
    if not providers:
        logger.error("❌ No valid providers created. Check your model names and API keys.")
        sys.exit(1)
    
    # Print configuration
    print_configuration(args, providers, logger)
    
    # Dry run check
    if args.dry_run:
        print("🏃‍♂️ Dry run completed. Configuration looks good!")
        return
    
    try:
        # Run evaluation
        results = await run_evaluation(args, providers, logger)
        
        # Print summary
        print_results_summary(results)
        
        # Generate reports
        report_files = generate_reports(results, args, logger)
        
        if report_files:
            print("🎉 Benchmark completed successfully!")
            print(f"📋 Reports generated: {len(report_files)} files")
            for filepath in report_files:
                print(f"   • {filepath}")
        else:
            print("⚠️  Benchmark completed but report generation failed")
        
    except KeyboardInterrupt:
        logger.info("❌ Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Benchmark failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())