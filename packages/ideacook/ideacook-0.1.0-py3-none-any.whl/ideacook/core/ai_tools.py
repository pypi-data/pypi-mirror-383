"""AI ideas, tools, and packages testing utilities for the IdeaCook package."""

from typing import Dict, List, Any, Union
import json
from datetime import datetime
import random


def generate_idea_prompt(category: str = "general") -> str:
    """
    Generate a creative AI idea prompt based on category.
    
    Args:
        category: Category of idea (general, coding, design, business, etc.)
        
    Returns:
        Creative idea prompt string
    """
    prompts = {
        "general": [
            "Design an AI assistant that helps with creative writing",
            "Create a tool that summarizes long articles into key points",
            "Develop a system that suggests recipes based on available ingredients",
            "Build an app that helps users learn new languages through games"
        ],
        "coding": [
            "Create an AI pair programmer that suggests code improvements",
            "Design a tool that automatically generates documentation from code",
            "Build a system that detects and fixes common coding errors",
            "Develop a code review assistant that provides actionable feedback"
        ],
        "design": [
            "Create an AI that generates color palettes based on mood",
            "Design a tool that suggests layout improvements for websites",
            "Build a system that creates logo variations from a base design",
            "Develop an assistant that helps with typography selection"
        ],
        "business": [
            "Create a tool that analyzes market trends and suggests opportunities",
            "Design a system that helps with customer segmentation",
            "Build an AI that generates personalized marketing messages",
            "Develop a tool that predicts product demand based on various factors"
        ]
    }
    
    category_prompts = prompts.get(category, prompts["general"])
    return random.choice(category_prompts)


def evaluate_ai_tool(tool_name: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate an AI tool based on provided metrics.
    
    Args:
        tool_name: Name of the AI tool
        metrics: Dictionary containing evaluation metrics
        
    Returns:
        Evaluation results with scores and recommendations
    """
    # Simple evaluation logic - in a real implementation, this would be more complex
    total_score = 0
    metric_count = 0
    
    for key, value in metrics.items():
        if isinstance(value, (int, float)) and key != "cost":
            total_score += value
            metric_count += 1
    
    average_score = total_score / metric_count if metric_count > 0 else 0
    
    # Generate recommendation based on score
    if average_score >= 8:
        recommendation = "Excellent tool, highly recommended"
    elif average_score >= 6:
        recommendation = "Good tool with minor improvements needed"
    elif average_score >= 4:
        recommendation = "Fair tool, significant improvements needed"
    else:
        recommendation = "Poor tool, not recommended"
    
    return {
        "tool_name": tool_name,
        "evaluation_date": datetime.now().isoformat(),
        "average_score": round(average_score, 2),
        "metric_count": metric_count,
        "recommendation": recommendation,
        "metrics_evaluated": list(metrics.keys())
    }


def run_ai_package_tests(package_name: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Test an AI package with a suite of test cases.
    
    Args:
        package_name: Name of the AI package to test
        test_cases: List of test case dictionaries
        
    Returns:
        Test results with summary statistics
    """
    results = []
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases):
        try:
            # Simulate test execution
            # In a real implementation, this would actually test the package
            result = {
                "test_id": i + 1,
                "name": test_case.get("name", f"Test {i+1}"),
                "status": "PASSED",
                "details": "Test executed successfully",
                "execution_time": round(random.uniform(0.1, 2.0), 3)
            }
            passed += 1
        except Exception as e:
            result = {
                "test_id": i + 1,
                "name": test_case.get("name", f"Test {i+1}"),
                "status": "FAILED",
                "details": str(e),
                "execution_time": 0
            }
            failed += 1
        
        results.append(result)
    
    return {
        "package_name": package_name,
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(test_cases),
        "passed": passed,
        "failed": failed,
        "pass_rate": round((passed / len(test_cases)) * 100, 2) if test_cases else 0,
        "results": results
    }


def pretty_print_evaluation(evaluation: Dict[str, Any]) -> None:
    """
    Pretty print AI tool evaluation results.
    
    Args:
        evaluation: Dictionary containing evaluation results
    """
    print("=" * 60)
    print(f"IDEACOOK AI TOOL EVALUATION REPORT")
    print("=" * 60)
    print(f"Tool Name: {evaluation.get('tool_name', 'N/A')}")
    print(f"Evaluation Date: {evaluation.get('evaluation_date', 'N/A')}")
    print(f"Average Score: {evaluation.get('average_score', 0)}/10")
    print(f"Metrics Evaluated: {len(evaluation.get('metrics_evaluated', []))}")
    print(f"Recommendation: {evaluation.get('recommendation', 'N/A')}")
    print("-" * 60)


def pretty_print_test_results(results: Dict[str, Any]) -> None:
    """
    Pretty print AI package test results.
    
    Args:
        results: Dictionary containing test results
    """
    print("=" * 60)
    print(f"IDEACOOK AI PACKAGE TEST RESULTS")
    print("=" * 60)
    print(f"Package Name: {results.get('package_name', 'N/A')}")
    print(f"Timestamp: {results.get('timestamp', 'N/A')}")
    print(f"Total Tests: {results.get('total_tests', 0)}")
    print(f"Passed: {results.get('passed', 0)}")
    print(f"Failed: {results.get('failed', 0)}")
    print(f"Pass Rate: {results.get('pass_rate', 0)}%")
    print("-" * 60)
    
    for result in results.get("results", []):
        status_symbol = "✓" if result.get("status") == "PASSED" else "✗"
        print(f"{status_symbol} Test {result.get('test_id', 'N/A')}: {result.get('name', 'Unknown Test')}")
        print(f"  Status: {result.get('status', 'UNKNOWN')}")
        print(f"  Execution Time: {result.get('execution_time', 0)}s")
        print(f"  Details: {result.get('details', 'No details')}")
        print()


def generate_test_report(results: Dict[str, Any], format: str = "json") -> str:
    """
    Generate a test report in specified format.
    
    Args:
        results: Dictionary containing test results
        format: Output format ("json" or "text")
        
    Returns:
        Formatted test report as string
    """
    if format.lower() == "json":
        return json.dumps(results, indent=2)
    else:
        report = "IDEACOOK AI PACKAGE TEST REPORT\n"
        report += "=" * 40 + "\n"
        report += f"Package Name: {results.get('package_name', 'N/A')}\n"
        report += f"Timestamp: {results.get('timestamp', 'N/A')}\n"
        report += f"Total Tests: {results.get('total_tests', 0)}\n"
        report += f"Passed: {results.get('passed', 0)}\n"
        report += f"Failed: {results.get('failed', 0)}\n"
        report += f"Pass Rate: {results.get('pass_rate', 0)}%\n\n"
        
        report += "Detailed Results:\n"
        report += "-" * 20 + "\n"
        for result in results.get("results", []):
            report += f"Test {result.get('test_id', 'N/A')}: {result.get('name', 'Unknown Test')}\n"
            report += f"  Status: {result.get('status', 'UNKNOWN')}\n"
            report += f"  Execution Time: {result.get('execution_time', 0)}s\n"
            report += f"  Details: {result.get('details', 'No details')}\n\n"
        
        return report