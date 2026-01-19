"""Quick test script for Interview Agent."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import InterviewAgent
from src.utils.config import Config
from tests.test_samples import SAMPLE_CASE_1, SAMPLE_CASE_2, SAMPLE_CASE_3, SAMPLE_CASE_4


def test_case(agent: InterviewAgent, case_name: str, case_text: str) -> None:
    """Test a single case.

    Args:
        agent: InterviewAgent instance
        case_name: Name of the test case
        case_text: Interview experience text
    """
    print(f"\n{'='*60}")
    print(f"Testing: {case_name}")
    print(f"{'='*60}\n")

    result = agent.process(
        input_data=case_text,
        generate_answers=False,
        export_format="both",
        output_filename=case_name.lower().replace(" ", "_"),
    )

    if result.success:
        print(f"✓ Success! Processing time: {result.processing_time:.2f}s")
        exp = result.experience
        print(f"  - Company: {exp.company_name or 'N/A'}")
        print(f"  - Position: {exp.position or 'N/A'}")
        print(f"  - Questions: {len(exp.questions)}")
        print(f"  - Tags: {', '.join(exp.tags)}")
    else:
        print(f"✗ Failed: {result.error}")


def main() -> None:
    """Main test function."""
    print("Interview Agent - Quick Test")
    print("="*60)

    # Load config
    try:
        config = Config.from_env()
    except Exception as e:
        print(f"Error loading config: {e}")
        print("\nPlease ensure .env file exists with valid SILICONFLOW_API_KEY")
        return

    # Verify API key
    if not config.siliconflow_api_key or config.siliconflow_api_key == "your_api_key_here":
        print("Error: SILICONFLOW_API_KEY not configured in .env")
        return

    # Initialize agent
    agent = InterviewAgent(config)

    # Run test cases
    test_cases = [
        ("Case 1 - Questions Only", SAMPLE_CASE_1),
        ("Case 2 - With Answers", SAMPLE_CASE_2),
        ("Case 3 - Complex Structured", SAMPLE_CASE_3),
        ("Case 4 - Simple List", SAMPLE_CASE_4),
    ]

    for case_name, case_text in test_cases:
        try:
            test_case(agent, case_name, case_text)
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
            break
        except Exception as e:
            print(f"✗ Error: {e}")

    print(f"\n{'='*60}")
    print("Test completed! Check the output/ directory for results.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
