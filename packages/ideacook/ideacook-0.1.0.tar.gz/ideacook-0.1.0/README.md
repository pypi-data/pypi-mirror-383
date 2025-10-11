# IdeaCook

[![PyPI version](https://badge.fury.io/py/ideacook.svg)](https://badge.fury.io/py/ideacook)
[![Python Version](https://img.shields.io/pypi/pyversions/ideacook)](https://pypi.org/project/ideacook/)
[![License](https://img.shields.io/pypi/l/ideacook)](https://github.com/ideacook/ideacook/blob/main/LICENSE)

**IdeaCook** is a comprehensive AI ideas, tools, and packages testing package with advanced pretty print features. It provides intuitive tools for generating creative AI ideas, evaluating AI tools, testing AI packages, and presenting results in beautifully formatted output.

## Features

- 🧠 **AI Idea Generation**: Generate creative prompts for various domains
- 📊 **AI Tool Evaluation**: Comprehensive evaluation framework for AI tools
- 🧪 **AI Package Testing**: Robust testing suite for AI packages
- 🎨 **Pretty Print Results**: Beautifully formatted output for easy analysis
- 📈 **Detailed Reporting**: Generate comprehensive reports in multiple formats
- ⚡ **High Performance**: Optimized for speed and efficiency
- 🛠️ **Easy Integration**: Simple API that integrates seamlessly with existing workflows
- 📦 **Lightweight**: Minimal dependencies with maximum functionality

## Installation

```bash
pip install ideacook
```

## Quick Start

### Basic Usage

```python
from ideacook import greet

# Simple greeting
print(greet("Developer"))
# Output: Hello, Developer! Welcome to IdeaCook.
```

### AI Idea Generation

```python
from ideacook import generate_idea_prompt

# Generate a random AI idea
idea = generate_idea_prompt()
print(f"AI Idea: {idea}")

# Generate an idea for a specific category
coding_idea = generate_idea_prompt("coding")
print(f"Coding Idea: {coding_idea}")
```

### AI Tool Evaluation

```python
from ideacook import evaluate_ai_tool, pretty_print_evaluation

# Define metrics for evaluation
tool_metrics = {
    "accuracy": 8.5,
    "speed": 7.2,
    "usability": 9.1,
    "reliability": 8.8,
    "cost": 2.5  # Lower is better for cost
}

# Evaluate an AI tool
evaluation = evaluate_ai_tool("Sample AI Tool", tool_metrics)

# Pretty print the evaluation
pretty_print_evaluation(evaluation)
```

### AI Package Testing

```python
from ideacook import test_ai_package, pretty_print_test_results

# Define your test cases
test_cases = [
    {
        "name": "Basic Functionality Test",
        "input": {"function": "process", "data": "sample"},
        "expected": {"result": "success"}
    },
    {
        "name": "Edge Case Handling",
        "input": {"function": "process", "data": ""},
        "expected": {"result": "handled"}
    }
]

# Test an AI package
results = test_ai_package("Sample AI Package", test_cases)

# Pretty print the results
pretty_print_test_results(results)
```

### Generating Reports

```python
from ideacook import generate_test_report

# Generate a JSON report
json_report = generate_test_report(results, format="json")
print(json_report)

# Generate a text report
text_report = generate_test_report(results, format="text")
print(text_report)
```

## API Reference

### Core Functions

#### `greet(name: str) -> str`
Returns a friendly greeting message.

#### `generate_idea_prompt(category: str = "general") -> str`
Generates a creative AI idea prompt based on the specified category.

#### `evaluate_ai_tool(tool_name: str, metrics: Dict[str, Any]) -> Dict[str, Any]`
Evaluates an AI tool based on provided metrics and returns detailed results.

#### `test_ai_package(package_name: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]`
Tests an AI package with a suite of test cases and returns detailed results.

#### `pretty_print_evaluation(evaluation: Dict[str, Any]) -> None`
Displays AI tool evaluation results in a beautifully formatted way.

#### `pretty_print_test_results(results: Dict[str, Any]) -> None`
Displays AI package test results in a beautifully formatted way.

#### `generate_test_report(results: Dict[str, Any], format: str = "json") -> str`
Generates a test report in the specified format (JSON or text).

### Project Information

#### `get_project_name() -> str`
Returns the project name.

#### `get_version() -> str`
Returns the current version.

#### `get_author() -> str`
Returns the author name.

#### `get_description() -> str`
Returns the project description.

#### `get_license() -> str`
Returns the project license.

#### `get_python_version() -> str`
Returns the minimum required Python version.

#### `get_project_url() -> str`
Returns the project homepage URL.

## Requirements

- Python >= 3.9
- No external dependencies

## Contributing

We welcome contributions to IdeaCook! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

1. Fork the repository
2. Create a new branch for your feature
3. Add your feature or improvement
4. Write tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please [file an issue](https://github.com/ideacook/ideacook/issues) on our GitHub repository.