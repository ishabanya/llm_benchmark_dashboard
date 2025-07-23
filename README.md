# 🤖 LLM Benchmark Framework

**A Production-Ready LLM Evaluation System**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)

---

## 🎯 Overview

This comprehensive LLM evaluation framework provides enterprise-grade benchmarking capabilities for Large Language Models. Built with deep understanding of LLM challenges and excellent engineering practices for professional evaluation needs.

### ✨ Key Features

- **🔌 Multi-Provider Support**: OpenAI (GPT-4, GPT-3.5), Anthropic (Claude), Ollama (Local Models)
- **📊 5 Evaluation Categories**: Factual Accuracy, Reasoning & Logic, Code Generation, Safety & Bias, Instruction Following
- **🎯 75+ Test Cases**: Comprehensive coverage across easy/medium/hard difficulty levels
- **⚡ Parallel Processing**: Async execution with configurable concurrency limits
- **💰 Cost Analysis**: Real-time cost tracking with efficiency scoring
- **📈 Statistical Analysis**: Confidence intervals, effect sizes, significance testing
- **🎨 Beautiful Dashboard**: Professional Streamlit web interface
- **📋 Multiple Export Formats**: HTML, JSON, CSV reports
- **💾 Smart Caching**: TTL-based caching to avoid expensive re-runs
- **🔒 Production Ready**: Comprehensive error handling, logging, Docker support

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd llm_bench

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Configuration

Add your API keys to `.env`:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Run Demo

```bash
# Run comprehensive demo
python demo.py

# Start web dashboard
streamlit run web_ui/app.py
```

---

## 🏗️ Architecture

```
llm_bench/
├── src/
│   ├── models/          # LLM provider implementations
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── ollama_provider.py
│   │   └── factory.py
│   ├── evaluators/      # Evaluation metrics
│   │   ├── factual_accuracy.py
│   │   ├── reasoning_logic.py
│   │   ├── code_generation.py
│   │   ├── safety_bias.py
│   │   └── instruction_following.py
│   ├── datasets/        # Test case collections
│   │   ├── factual_accuracy_data.py
│   │   ├── reasoning_logic_data.py
│   │   └── [...]
│   ├── core/           # Main evaluation engine
│   │   ├── runner.py   # Parallel evaluation runner
│   │   ├── metrics.py  # Statistical analysis
│   │   └── cache.py    # Result caching
│   └── reporters/      # Report generation
│       ├── html_reporter.py
│       ├── json_reporter.py
│       └── csv_reporter.py
├── web_ui/
│   └── app.py          # Streamlit dashboard
├── tests/              # Unit tests
├── examples/           # Usage examples
└── config/            # Configuration files
```

---

## 📊 Evaluation Categories

### 1. **Factual Accuracy**
Tests knowledge across domains with verifiable answers
- **Easy**: Basic facts (capitals, famous people)
- **Medium**: Specific knowledge (atomic numbers, dates)
- **Hard**: Specialized knowledge (molecular formulas, rare facts)

### 2. **Reasoning & Logic**
Evaluates logical thinking and problem-solving
- **Easy**: Simple syllogisms, basic math
- **Medium**: Probability, puzzles, algebra
- **Hard**: Paradoxes, advanced math, complex reasoning

### 3. **Code Generation**
Assesses Python programming capabilities
- **Easy**: Basic functions, loops
- **Medium**: Algorithms, data structures
- **Hard**: Advanced patterns, complex implementations

### 4. **Safety & Bias Detection**
Tests safety measures and bias awareness
- **Harmful Content**: Refusal of dangerous requests
- **Bias Detection**: Avoiding stereotypes and discrimination
- **Ethical Reasoning**: Moral decision-making

### 5. **Instruction Following**
Evaluates adherence to complex, multi-step instructions
- **Format Compliance**: Word counts, structure requirements
- **Constraint Satisfaction**: Specific limitations and rules
- **Multi-step Tasks**: Complex sequential instructions

---

## 🎨 Web Dashboard

The Streamlit dashboard provides:

- **📊 Real-time Evaluation**: Watch progress as tests run
- **🏆 Interactive Rankings**: Compare model performance
- **💰 Cost Analysis**: Track spending and efficiency
- **📈 Statistical Insights**: Confidence intervals, significance
- **📋 Export Options**: Generate reports in multiple formats
- **🎨 Professional UI**: Modern, responsive design

### Dashboard Screenshots

*[Screenshots would be inserted here in a real README]*

---

## 📈 Metrics & Analysis

### Performance Metrics
- **Overall Score**: 0-100 normalized performance score
- **Pass Rate**: Percentage of tests passed (≥70% threshold)
- **Category Breakdown**: Performance across evaluation dimensions
- **Difficulty Analysis**: Easy/Medium/Hard performance comparison

### Cost Analysis
- **Total Cost**: USD spent across all providers
- **Cost per Evaluation**: Average cost per test case
- **Cost Efficiency**: Performance per dollar spent
- **Token Usage**: Input/output token consumption

### Statistical Analysis
- **Confidence Intervals**: 95% CI for score estimates
- **Effect Sizes**: Cohen's d for provider comparisons
- **Reliability Scores**: Consistency and error rate analysis
- **Distribution Analysis**: Skewness, kurtosis, variance

---

## 🔧 Advanced Usage

### Custom Model Configuration

```python
from models.factory import ModelFactory
from models.base import ModelConfig

# Configure custom model
config = ModelConfig(
    model_name="gpt-4o",
    provider="openai",
    temperature=0.7,
    max_tokens=1000,
    cost_per_input_token=0.005,
    cost_per_output_token=0.015
)

provider = ModelFactory.create_provider(config)
```

### Custom Evaluation

```python
from core.runner import EvaluationRunner

runner = EvaluationRunner(
    cache_enabled=True,
    max_concurrent=5
)

results = await runner.run_evaluation(
    providers=[provider],
    categories=["factual_accuracy", "reasoning_logic"],
    difficulties=["medium", "hard"],
    max_cases_per_category=10
)
```

### Custom Test Cases

```python
from evaluators.base import TestCase
from datasets.base import TestCaseLoader

# Create custom test case
test_case = TestCaseLoader.create_test_case(
    test_id="custom_001",
    category="factual_accuracy",
    subcategory="science",
    difficulty="medium",
    prompt="What is the speed of light?",
    expected_answer="299,792,458 m/s"
)
```

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t llm-bench .

# Run container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_key \
  -e ANTHROPIC_API_KEY=your_key \
  llm-bench

# Access dashboard at http://localhost:8501
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test category
pytest tests/test_evaluators.py -v
```

---

## 📋 Report Formats

### HTML Report
- Interactive Plotly charts
- Professional styling with CSS
- Comprehensive analysis sections
- Mobile-responsive design

### JSON Report
- Complete raw data export
- Programmatic access to all metrics
- Structured for further analysis
- API integration ready

### CSV Report
- Tabular data for spreadsheet analysis
- Per-test-case detailed results
- Summary statistics included
- Database import friendly

---

## 🎯 Model Recommendation Engine

The framework includes an intelligent recommendation system:

### Use Case Recommendations
- **Research**: Prioritizes accuracy and reasoning
- **Production**: Balances performance with cost
- **Creative Tasks**: Emphasizes instruction following
- **Safety-Critical**: Prioritizes safety and bias scores

### Efficiency Scoring
- **Cost Efficiency**: Performance per dollar
- **Speed Efficiency**: Performance per second
- **Overall Efficiency**: Weighted combination

---

## 🔍 Key Insights Generated

- **Performance Leaders**: Top-performing models by category
- **Cost Champions**: Best value propositions
- **Reliability Analysis**: Consistency and error patterns
- **Category Strengths**: Where each model excels
- **Difficulty Scaling**: Performance across complexity levels

---

## 🛠️ Development

### Adding New Providers

1. Create provider class inheriting from `LLMProvider`
2. Implement required methods: `generate()`, `is_available()`, `get_model_info()`
3. Register in `ModelFactory`
4. Add to provider selection in web interface

### Adding New Evaluators

1. Create evaluator class inheriting from `Evaluator`
2. Implement `evaluate()` method with scoring logic
3. Create corresponding dataset with test cases
4. Register in evaluation runner

### Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

---

## 📊 Sample Output

```
🏆 PROVIDER RANKINGS:
   🥇 gpt-4o: 89.3 points
   🥈 claude-3-sonnet: 86.7 points  
   🥉 llama2-7b: 74.2 points

💰 COST ANALYSIS:
   Total Cost: $0.0432
   Avg Performance: 83.4
   Avg Latency: 1460ms

⚡ EFFICIENCY CHAMPION:
   claude-3-sonnet (Score: 95.1)
```

---

## 🎓 Educational Value

This project demonstrates:

- **System Design**: Modular, extensible architecture
- **Async Programming**: Efficient concurrent processing
- **Data Analysis**: Statistical methods and visualization
- **Web Development**: Modern UI with Streamlit
- **Testing**: Comprehensive test coverage
- **Documentation**: Clear, professional documentation
- **Production Readiness**: Error handling, logging, caching

---

## 🚀 Future Enhancements

- **Multi-modal Evaluation**: Image and audio capabilities
- **Custom Metrics**: User-defined evaluation criteria
- **A/B Testing**: Statistical significance testing
- **Real-time Monitoring**: Live performance tracking
- **Model Fine-tuning**: Integration with training pipelines
- **Enterprise Features**: SSO, audit logs, compliance

---

## 📞 Contact

**Contact**
- 📧 Email: [contact@example.com]
- 💼 LinkedIn: [linkedin.com/in/shabanya]
- 🐙 GitHub: [github.com/ishabanya]

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ - Professional LLM evaluation capabilities for enterprise use**