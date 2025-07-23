"""Streamlit web dashboard for LLM benchmarking."""

import streamlit as st
import asyncio
import os
import sys
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.factory import ModelFactory
from models.base import ModelConfig
from core.runner import EvaluationRunner
from datasets.loader import DatasetLoader
from reporters.json_reporter import JSONReporter
from reporters.html_reporter import HTMLReporter
from reporters.csv_reporter import CSVReporter
from core.logger import setup_logger

# Page configuration
st.set_page_config(
    page_title="LLM Benchmark Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = setup_logger("streamlit_app", console_output=False)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .sidebar .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
    
    .evaluation-progress {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)


class LLMBenchmarkDashboard:
    """Main dashboard class for LLM benchmarking."""
    
    def __init__(self):
        self.initialize_session_state()
        self.logger = logger
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'evaluation_running' not in st.session_state:
            st.session_state.evaluation_running = False
        
        if 'evaluation_results' not in st.session_state:
            st.session_state.evaluation_results = None
        
        if 'cached_providers' not in st.session_state:
            st.session_state.cached_providers = {}
        
        if 'progress_data' not in st.session_state:
            st.session_state.progress_data = {"progress": 0, "message": "Ready"}
        
        # Auto-load sample data for demonstration purposes (especially for deployed version)
        if 'sample_data_loaded' not in st.session_state:
            st.session_state.sample_data_loaded = False
            if st.session_state.evaluation_results is None:
                self.load_sample_results_silently()
                st.session_state.sample_data_loaded = True
    
    def run(self):
        """Main dashboard application."""
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🤖 LLM Benchmark Dashboard</h1>
            <p>Production-Ready LLM Evaluation Framework</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar configuration
        self.render_sidebar()
        
        # Main content
        if st.session_state.evaluation_results is None:
            self.render_configuration_page()
        else:
            self.render_results_page()
    
    def render_sidebar(self):
        """Render the sidebar with configuration options."""
        st.sidebar.title("⚙️ Configuration")
        
        # API Keys section
        st.sidebar.subheader("🔐 API Keys")
        
        openai_key = st.sidebar.text_input(
            "OpenAI API Key",
            type="password",
            help="Required for OpenAI models (GPT-4, GPT-3.5, etc.)"
        )
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        
        anthropic_key = st.sidebar.text_input(
            "Anthropic API Key", 
            type="password",
            help="Required for Claude models"
        )
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        
        ollama_url = st.sidebar.text_input(
            "Ollama Base URL",
            value="http://localhost:11434",
            help="URL for local Ollama instance"
        )
        if ollama_url:
            os.environ["OLLAMA_BASE_URL"] = ollama_url
        
        st.sidebar.divider()
        
        # Model selection
        st.sidebar.subheader("🤖 Model Selection")
        
        selected_models = st.sidebar.multiselect(
            "Choose Models to Evaluate",
            options=[
                "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo",
                "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
                "llama2:13b", "llama2:7b", "codellama:7b"
            ],
            default=["gpt-4o", "claude-3-sonnet"],
            help="Select models to include in the benchmark"
        )
        
        st.session_state.selected_models = selected_models
        
        st.sidebar.divider()
        
        # Evaluation settings
        st.sidebar.subheader("📊 Evaluation Settings")
        
        categories = st.sidebar.multiselect(
            "Test Categories",
            options=DatasetLoader.get_available_categories(),
            default=DatasetLoader.get_available_categories(),
            help="Select which evaluation categories to include"
        )
        
        difficulties = st.sidebar.multiselect(
            "Difficulty Levels",
            options=["easy", "medium", "hard"],
            default=["easy", "medium", "hard"],
            help="Select difficulty levels to include"
        )
        
        max_cases = st.sidebar.slider(
            "Max Cases per Category",
            min_value=1,
            max_value=25,
            value=10,
            help="Limit test cases per category for faster evaluation"
        )
        
        st.session_state.eval_config = {
            "categories": categories,
            "difficulties": difficulties,
            "max_cases_per_category": max_cases
        }
        
        st.sidebar.divider()
        
        # Quick actions
        st.sidebar.subheader("🚀 Quick Actions")
        
        if st.sidebar.button("🏃‍♂️ Quick Benchmark", use_container_width=True):
            st.session_state.run_quick_benchmark = True
        
        if st.sidebar.button("🧹 Clear Cache", use_container_width=True):
            self.clear_cache()
            st.success("Cache cleared!")
        
        if st.sidebar.button("📥 Load Sample Results", use_container_width=True):
            self.load_sample_results()
    
    def render_configuration_page(self):
        """Render the main configuration and evaluation page."""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🎯 Benchmark Configuration")
            
            # Dataset overview
            dataset_summary = DatasetLoader.get_dataset_summary()
            
            st.info(f"""
            **Dataset Overview:**
            - 📝 Total Test Cases: {dataset_summary['total_test_cases']}
            - 📊 Categories: {len(dataset_summary['datasets'])}
            - 🎚️ Difficulty Levels: {', '.join(dataset_summary['difficulty_distribution'].keys())}
            """)
            
            # Model configuration
            if st.session_state.selected_models:
                st.success(f"✅ {len(st.session_state.selected_models)} models selected for evaluation")
                
                # Display selected models
                for model in st.session_state.selected_models:
                    provider = self.get_provider_from_model(model)
                    st.write(f"• **{model}** ({provider})")
            else:
                st.warning("⚠️ Please select at least one model to evaluate")
            
            # Evaluation configuration display
            eval_config = st.session_state.eval_config
            st.write(f"""
            **Evaluation Configuration:**
            - Categories: {len(eval_config['categories'])} selected
            - Difficulties: {', '.join(eval_config['difficulties'])}
            - Max cases per category: {eval_config['max_cases_per_category']}
            """)
            
            # Estimated cost and time
            estimated_tests = self.estimate_test_count()
            st.write(f"📈 **Estimated Tests:** {estimated_tests}")
            
        with col2:
            st.subheader("🚀 Start Evaluation")
            
            # Quick benchmark button
            if st.button("🏃‍♂️ Run Quick Benchmark (3 cases/category)", 
                        use_container_width=True, type="primary"):
                if st.session_state.selected_models:
                    self.run_evaluation(quick=True)
                else:
                    st.error("Please select at least one model first!")
            
            # Full benchmark button
            if st.button("🔥 Run Full Benchmark", 
                        use_container_width=True):
                if st.session_state.selected_models:
                    self.run_evaluation(quick=False)
                else:
                    st.error("Please select at least one model first!")
            
            st.divider()
            
            # Cache status
            self.display_cache_status()
        
        # Progress display
        if st.session_state.evaluation_running:
            self.display_evaluation_progress()
    
    def render_results_page(self):
        """Render the results analysis page."""
        if st.session_state.evaluation_results is None:
            st.error("No evaluation results available")
            return
        
        results = st.session_state.evaluation_results
        
        # Results header with metadata
        metadata = results.get("metadata", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Evaluations",
                metadata.get("total_evaluations", 0),
                help="Total number of model-test combinations evaluated"
            )
        
        with col2:
            duration = metadata.get("evaluation_time_seconds", 0)
            st.metric(
                "Evaluation Time",
                f"{duration:.1f}s",
                help="Total time taken for evaluation"
            )
        
        with col3:
            providers_tested = len(metadata.get("providers_tested", []))
            st.metric(
                "Models Tested",
                providers_tested,
                help="Number of models evaluated"
            )
        
        with col4:
            categories_tested = len(metadata.get("categories_tested", []))
            st.metric(
                "Categories",
                categories_tested,
                help="Number of evaluation categories"
            )
        
        st.divider()
        
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", "🏆 Rankings", "💰 Cost Analysis", 
            "📈 Detailed Metrics", "📋 Export Results"
        ])
        
        with tab1:
            self.render_overview_tab(results)
        
        with tab2:
            self.render_rankings_tab(results)
        
        with tab3:
            self.render_cost_analysis_tab(results)
        
        with tab4:
            self.render_detailed_metrics_tab(results)
        
        with tab5:
            self.render_export_tab(results)
    
    def render_overview_tab(self, results: Dict[str, Any]):
        """Render the overview tab with key visualizations."""
        summary = results.get("summary", {})
        metrics = results.get("metrics", {})
        
        # Provider performance comparison
        st.subheader("🏆 Provider Performance Comparison")
        
        provider_summaries = summary.get("provider_summaries", {})
        if provider_summaries:
            df_providers = pd.DataFrame.from_dict(provider_summaries, orient='index')
            df_providers.index.name = 'Provider'
            df_providers = df_providers.reset_index()
            
            fig = px.bar(
                df_providers, 
                x='Provider', 
                y='overall_score',
                title="Average Score by Provider",
                color='overall_score',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Category performance
            st.subheader("📊 Performance by Category")
            
            category_metrics = metrics.get("category_metrics", {})
            if category_metrics:
                categories = list(category_metrics.keys())
                scores = [category_metrics[cat]["average_score"] for cat in categories]
                
                fig = px.pie(
                    values=scores,
                    names=categories,
                    title="Score Distribution by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Difficulty analysis
            st.subheader("🎯 Performance by Difficulty")
            
            difficulty_metrics = metrics.get("difficulty_metrics", {})
            if difficulty_metrics:
                difficulties = list(difficulty_metrics.keys())
                scores = [difficulty_metrics[diff]["average_score"] for diff in difficulties]
                
                fig = px.bar(
                    x=difficulties,
                    y=scores,
                    title="Average Score by Difficulty",
                    color=scores,
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def render_rankings_tab(self, results: Dict[str, Any]):
        """Render the rankings tab."""
        st.subheader("🏆 Model Rankings")
        
        summary = results.get("summary", {})
        provider_rankings = summary.get("provider_rankings", [])
        
        if provider_rankings:
            # Overall rankings
            st.write("### Overall Performance Rankings")
            
            for i, ranking in enumerate(provider_rankings, 1):
                col1, col2, col3 = st.columns([1, 4, 2])
                
                with col1:
                    if i == 1:
                        st.markdown("🥇")
                    elif i == 2:
                        st.markdown("🥈")
                    elif i == 3:
                        st.markdown("🥉")
                    else:
                        st.markdown(f"**{i}.**")
                
                with col2:
                    st.markdown(f"**{ranking['provider']}**")
                
                with col3:
                    score = ranking['score']
                    color = "green" if score >= 80 else "orange" if score >= 60 else "red"
                    st.markdown(f"<span style='color: {color}'>{score:.1f}</span>", 
                              unsafe_allow_html=True)
        
        # Category-specific rankings
        st.write("### Category-Specific Rankings")
        
        metrics = results.get("metrics", {})
        category_metrics = metrics.get("category_metrics", {})
        
        for category, cat_metrics in category_metrics.items():
            st.write(f"#### {category.replace('_', ' ').title()}")
            
            provider_performance = cat_metrics.get("provider_performance", {})
            if provider_performance:
                sorted_providers = sorted(
                    provider_performance.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for i, (provider, score) in enumerate(sorted_providers, 1):
                    st.write(f"{i}. **{provider}**: {score:.1f}")
    
    def render_cost_analysis_tab(self, results: Dict[str, Any]):
        """Render the cost analysis tab."""
        st.subheader("💰 Cost Analysis")
        
        # Show sample data indicator if using demo data
        if st.session_state.get('sample_data_loaded', False) and st.session_state.evaluation_results:
            st.info("📊 **Viewing Sample Data** - This is demonstration data. Run an actual evaluation to see real costs.")
        
        metrics = results.get("metrics", {})
        cost_analysis = metrics.get("cost_analysis", {})
        
        if not cost_analysis:
            st.warning("No cost analysis data available")
            return
        
        # Overall cost metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_cost = cost_analysis.get("total_cost_all_providers", 0)
            st.metric("Total Cost", f"${total_cost:.4f}")
        
        with col2:
            avg_cost = cost_analysis.get("average_cost_per_evaluation", 0)
            st.metric("Avg Cost/Evaluation", f"${avg_cost:.4f}")
        
        with col3:
            cost_dist = cost_analysis.get("cost_distribution", {})
            max_cost = cost_dist.get("max_cost", 0)
            st.metric("Most Expensive Test", f"${max_cost:.4f}")
        
        # Provider cost comparison
        st.write("### Cost by Provider")
        
        provider_cost_analysis = cost_analysis.get("provider_cost_analysis", {})
        if provider_cost_analysis:
            providers = list(provider_cost_analysis.keys())
            costs = [provider_cost_analysis[p]["total_cost"] for p in providers]
            efficiencies = [provider_cost_analysis[p]["cost_efficiency_ratio"] for p in providers]
            
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=("Total Cost by Provider", "Cost Efficiency Ratio")
            )
            
            fig.add_trace(
                go.Bar(x=providers, y=costs, name="Total Cost"),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(x=providers, y=efficiencies, name="Efficiency", marker_color="orange"),
                row=1, col=2
            )
            
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    def render_detailed_metrics_tab(self, results: Dict[str, Any]):
        """Render detailed metrics analysis."""
        st.subheader("📈 Detailed Metrics Analysis")
        
        metrics = results.get("metrics", {})
        
        # Provider metrics table
        st.write("### Provider Performance Metrics")
        
        provider_metrics = metrics.get("provider_metrics", {})
        if provider_metrics:
            df_metrics = pd.DataFrame.from_dict(provider_metrics, orient='index')
            
            # Select key columns for display
            display_columns = [
                'average_score', 'pass_rate', 'total_cost_usd', 
                'average_latency_ms', 'reliability_score'
            ]
            
            df_display = df_metrics[display_columns].round(3)
            df_display.columns = [
                'Avg Score', 'Pass Rate', 'Total Cost ($)', 
                'Avg Latency (ms)', 'Reliability'
            ]
            
            st.dataframe(df_display, use_container_width=True)
        
        # Performance vs cost scatter plot
        st.write("### Performance vs Cost Analysis")
        
        if provider_metrics:
            providers = list(provider_metrics.keys())
            scores = [provider_metrics[p]["average_score"] for p in providers]
            costs = [provider_metrics[p]["total_cost_usd"] for p in providers]
            
            fig = px.scatter(
                x=costs,
                y=scores,
                text=providers,
                title="Performance vs Cost",
                labels={"x": "Total Cost (USD)", "y": "Average Score"}
            )
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)
        
        # Statistical analysis
        st.write("### Statistical Analysis")
        
        statistical_analysis = metrics.get("statistical_analysis", {})
        if statistical_analysis:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Sample Statistics:**")
                st.write(f"- Sample Size: {statistical_analysis.get('sample_size', 0)}")
                
                ci = statistical_analysis.get('confidence_interval_95', {})
                if ci:
                    st.write(f"- 95% CI: [{ci.get('lower', 0):.2f}, {ci.get('upper', 0):.2f}]")
                
                cv = statistical_analysis.get('coefficient_of_variation', 0)
                st.write(f"- Coefficient of Variation: {cv:.2f}%")
            
            with col2:
                st.write("**Provider Comparisons:**")
                comparisons = statistical_analysis.get('provider_comparisons', {})
                for comparison, data in comparisons.items():
                    providers = comparison.replace('_vs_', ' vs ')
                    effect = data.get('effect_size_interpretation', 'unknown')
                    st.write(f"- {providers}: {effect} effect")
    
    def render_export_tab(self, results: Dict[str, Any]):
        """Render the export results tab."""
        st.subheader("📋 Export Results")
        
        st.write("Export your evaluation results in various formats:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export JSON", use_container_width=True):
                self.export_results(results, "json")
        
        with col2:
            if st.button("🌐 Export HTML", use_container_width=True):
                self.export_results(results, "html")
        
        with col3:
            if st.button("📊 Export CSV", use_container_width=True):
                self.export_results(results, "csv")
        
        st.divider()
        
        # Raw data preview
        st.write("### Raw Data Preview")
        
        if st.checkbox("Show raw evaluation data"):
            st.json(results, expanded=False)
    
    def run_evaluation(self, quick: bool = False):
        """Run the evaluation with selected models."""
        try:
            st.session_state.evaluation_running = True
            
            # Create progress placeholder
            progress_placeholder = st.empty()
            
            # Prepare providers
            providers = []
            for model_name in st.session_state.selected_models:
                try:
                    provider_name = self.get_provider_from_model(model_name)
                    config = ModelConfig(
                        model_name=model_name,
                        provider=provider_name,
                        temperature=0.7,
                        max_tokens=1000
                    )
                    provider = ModelFactory.create_provider(config)
                    providers.append(provider)
                except Exception as e:
                    st.error(f"Failed to create provider for {model_name}: {str(e)}")
                    continue
            
            if not providers:
                st.error("No valid providers created. Check your API keys and model selections.")
                st.session_state.evaluation_running = False
                return
            
            # Create runner with progress callback
            def progress_callback(message: str, progress: float):
                st.session_state.progress_data = {
                    "progress": progress,
                    "message": message
                }
                progress_placeholder.progress(progress, text=message)
            
            runner = EvaluationRunner(
                cache_enabled=True,
                max_concurrent=3,
                progress_callback=progress_callback
            )
            
            # Run evaluation
            eval_config = st.session_state.eval_config
            
            with st.spinner("Running evaluation..."):
                if quick:
                    results = asyncio.run(runner.run_quick_benchmark(
                        providers=providers,
                        num_cases_per_category=3
                    ))
                else:
                    results = asyncio.run(runner.run_evaluation(
                        providers=providers,
                        categories=eval_config["categories"],
                        difficulties=eval_config["difficulties"],
                        max_cases_per_category=eval_config["max_cases_per_category"]
                    ))
            
            st.session_state.evaluation_results = results
            st.session_state.evaluation_running = False
            
            st.success("✅ Evaluation completed successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Evaluation failed: {str(e)}")
            st.session_state.evaluation_running = False
            self.logger.error(f"Evaluation error: {str(e)}")
    
    def get_provider_from_model(self, model_name: str) -> str:
        """Get provider name from model name."""
        if model_name.startswith("gpt"):
            return "openai"
        elif model_name.startswith("claude"):
            return "anthropic"
        elif "llama" in model_name.lower() or "codellama" in model_name.lower():
            return "ollama"
        else:
            return "unknown"
    
    def estimate_test_count(self) -> int:
        """Estimate the number of tests that will be run."""
        eval_config = st.session_state.eval_config
        
        total_cases = 0
        for category in eval_config["categories"]:
            dataset = DatasetLoader.get_dataset(category)
            cases = dataset.get_test_cases()
            
            # Filter by difficulty
            filtered_cases = [
                case for case in cases 
                if case.difficulty in eval_config["difficulties"]
            ]
            
            # Apply max cases limit
            case_count = min(len(filtered_cases), eval_config["max_cases_per_category"])
            total_cases += case_count
        
        return total_cases * len(st.session_state.selected_models)
    
    def display_cache_status(self):
        """Display cache status information."""
        try:
            from core.cache import ResultCache
            cache = ResultCache()
            stats = cache.get_cache_stats()
            
            st.write("**Cache Status:**")
            st.write(f"- Entries: {stats.get('total_entries', 0)}")
            st.write(f"- Size: {stats.get('cache_size_mb', 0):.2f} MB")
            
        except Exception as e:
            st.write("Cache status unavailable")
    
    def clear_cache(self):
        """Clear the evaluation cache."""
        try:
            from core.cache import ResultCache
            cache = ResultCache()
            cache.clear_cache()
            return True
        except Exception as e:
            st.error(f"Failed to clear cache: {str(e)}")
            return False
    
    def display_evaluation_progress(self):
        """Display evaluation progress."""
        progress_data = st.session_state.progress_data
        
        st.markdown("""
        <div class="evaluation-progress">
            <h4>🔄 Evaluation in Progress</h4>
        </div>
        """, unsafe_allow_html=True)
        
        progress = progress_data.get("progress", 0)
        message = progress_data.get("message", "Processing...")
        
        st.progress(progress, text=message)
    
    def export_results(self, results: Dict[str, Any], format_type: str):
        """Export results in the specified format."""
        try:
            if format_type == "json":
                reporter = JSONReporter()
                filepath = reporter.generate_report(results)
                st.success(f"✅ JSON report saved to: {filepath}")
                
            elif format_type == "html":
                reporter = HTMLReporter()
                filepath = reporter.generate_report(results)
                st.success(f"✅ HTML report saved to: {filepath}")
                
            elif format_type == "csv":
                reporter = CSVReporter()
                filepath = reporter.generate_report(results)
                st.success(f"✅ CSV report saved to: {filepath}")
            
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")
    
    def load_sample_results(self):
        """Load sample results for demonstration."""
        try:
            # Create sample results data structure
            sample_results = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "evaluation_time_seconds": 45.2,
                    "total_evaluations": 30,
                    "providers_tested": ["gpt-4o", "claude-3-sonnet"],
                    "categories_tested": ["factual_accuracy", "reasoning_logic", "code_generation"]
                },
                "summary": {
                    "provider_summaries": {
                        "gpt-4o": {
                            "overall_score": 87.5,
                            "pass_rate": 0.85,
                            "total_cost_usd": 0.125,
                            "avg_latency_ms": 1250,
                            "tests_completed": 15,
                            "tests_passed": 13
                        },
                        "claude-3-sonnet": {
                            "overall_score": 84.2,
                            "pass_rate": 0.80,
                            "total_cost_usd": 0.098,
                            "avg_latency_ms": 980,
                            "tests_completed": 15,
                            "tests_passed": 12
                        }
                    },
                    "provider_rankings": [
                        {"provider": "gpt-4o", "score": 87.5},
                        {"provider": "claude-3-sonnet", "score": 84.2}
                    ],
                    "overall_statistics": {
                        "avg_score_all_providers": 85.85,
                        "total_cost_all_providers": 0.223,
                        "avg_latency_all_providers": 1115
                    }
                },
                "metrics": {
                    "provider_metrics": {
                        "gpt-4o": {
                            "average_score": 87.5,
                            "pass_rate": 0.85,
                            "total_cost_usd": 0.125,
                            "average_latency_ms": 1250,
                            "reliability_score": 0.92
                        },
                        "claude-3-sonnet": {
                            "average_score": 84.2,
                            "pass_rate": 0.80,
                            "total_cost_usd": 0.098,
                            "average_latency_ms": 980,
                            "reliability_score": 0.88
                        }
                    },
                    "category_metrics": {
                        "factual_accuracy": {"average_score": 89.0},
                        "reasoning_logic": {"average_score": 82.5},
                        "code_generation": {"average_score": 86.2}
                    },
                    "difficulty_metrics": {
                        "easy": {"average_score": 92.1},
                        "medium": {"average_score": 84.3},
                        "hard": {"average_score": 78.8}
                    },
                    "cost_analysis": {
                        "total_cost_all_providers": 0.223,
                        "average_cost_per_evaluation": 0.0074,
                        "provider_cost_analysis": {
                            "gpt-4o": {"total_cost": 0.125, "cost_efficiency_ratio": 700.0},
                            "claude-3-sonnet": {"total_cost": 0.098, "cost_efficiency_ratio": 859.2}
                        }
                    }
                }
            }
            
            st.session_state.evaluation_results = sample_results
            st.success("✅ Sample results loaded!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Failed to load sample results: {str(e)}")

    def load_sample_results_silently(self):
        """Load sample results silently for automatic initialization."""
        try:
            # Create sample results data structure (same as above but without UI feedback)
            sample_results = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "evaluation_time_seconds": 45.2,
                    "total_evaluations": 30,
                    "providers_tested": ["gpt-4o", "claude-3-sonnet"],
                    "categories_tested": ["factual_accuracy", "reasoning_logic", "code_generation"]
                },
                "results": {
                    "gpt-4o": {
                        "overall_score": 87.5,
                        "pass_rate": 0.85,
                        "total_evaluations": 15,
                        "average_latency_ms": 1250,
                        "reliability_score": 95.2,
                        "cost_analysis": {
                            "total_cost_usd": 0.125,
                            "cost_per_evaluation": 0.0083,
                            "cost_efficiency_ratio": 700.0
                        }
                    },
                    "claude-3-sonnet": {
                        "overall_score": 84.2,
                        "pass_rate": 0.82,
                        "total_evaluations": 15,
                        "average_latency_ms": 980,
                        "reliability_score": 92.8,
                        "cost_analysis": {
                            "total_cost_usd": 0.098,
                            "cost_per_evaluation": 0.0065,
                            "cost_efficiency_ratio": 859.2
                        }
                    }
                },
                "metrics": {
                    "summary": {
                        "total_cost_all_providers": 0.223,
                        "average_score_across_providers": 85.85,
                        "best_performing_provider": "gpt-4o",
                        "most_cost_effective_provider": "claude-3-sonnet",
                        "total_evaluation_time_minutes": 0.75
                    },
                    "individual_metrics": {
                        "gpt-4o": {
                            "overall_score": 87.5,
                            "pass_rate": 0.85,
                            "total_cost_usd": 0.125,
                            "average_latency_ms": 1250,
                            "reliability_score": 95.2
                        },
                        "claude-3-sonnet": {
                            "overall_score": 84.2,
                            "pass_rate": 0.82,
                            "total_cost_usd": 0.098,
                            "average_latency_ms": 980,
                            "reliability_score": 92.8
                        }
                    },
                    "cost_analysis": {
                        "total_cost_all_providers": 0.223,
                        "average_cost_per_evaluation": 0.0074,
                        "provider_cost_analysis": {
                            "gpt-4o": {"total_cost": 0.125, "cost_efficiency_ratio": 700.0},
                            "claude-3-sonnet": {"total_cost": 0.098, "cost_efficiency_ratio": 859.2}
                        }
                    }
                }
            }
            
            st.session_state.evaluation_results = sample_results
            
        except Exception as e:
            # Silently fail - no UI feedback for auto-loading
            pass


def main():
    """Main function to run the Streamlit app."""
    dashboard = LLMBenchmarkDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()