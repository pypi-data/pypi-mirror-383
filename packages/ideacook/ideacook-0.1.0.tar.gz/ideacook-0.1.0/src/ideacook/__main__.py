from . import (
    greet, 
    get_author, 
    get_project_name, 
    get_version,
    get_description,
    generate_idea_prompt,
    evaluate_ai_tool,
    run_ai_package_tests,
    pretty_print_test_results
)

def main():
    print("=== Project Info ===")
    print(f"Project Name: {get_project_name()}")
    print(f"Version: {get_version()}")
    print(f"Author: {get_author()}")
    print(f"Description: {get_description()}")
    
    print("\n=== Greet Example ===")
    print(greet("Victor"))
    
    print("\n=== AI Idea Generation Demo ===")
    idea = generate_idea_prompt("coding")
    print(f"Generated Idea: {idea}")
    
    print("\n=== AI Tool Evaluation Demo ===")
    tool_metrics = {
        "accuracy": 8.5,
        "speed": 7.2,
        "usability": 9.1,
        "reliability": 8.8
    }
    evaluation = evaluate_ai_tool("Sample AI Tool", tool_metrics)
    print(f"Tool Evaluation: {evaluation['tool_name']}")
    print(f"Average Score: {evaluation['average_score']}/10")
    print(f"Recommendation: {evaluation['recommendation']}")
    
    print("\n=== AI Package Testing Demo ===")
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
    
    results = run_ai_package_tests("Sample AI Package", test_cases)
    pretty_print_test_results(results)

if __name__ == "__main__":
    main()