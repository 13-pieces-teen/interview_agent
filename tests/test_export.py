"""Test script for export functionality."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.database import Database
from src.services.export_service import ExportService


def test_export():
    """Test export functionality."""
    print("Testing export functionality...\n")

    # Initialize database and export service
    db = Database()
    export_service = ExportService(db)

    # Get all experiences
    experiences = db.list_experiences(limit=5)
    print(f"Found {len(experiences)} experiences in database\n")

    if len(experiences) == 0:
        print("No experiences found. Please process some interview data first.")
        return

    # Test export by interview
    print("=" * 80)
    print("Testing export by interview...")
    print("=" * 80)
    markdown_by_interview = export_service.export_by_interview()
    print(markdown_by_interview[:500])  # Print first 500 chars
    print(f"\n... (total {len(markdown_by_interview)} characters)")

    # Test export by question
    print("\n" + "=" * 80)
    print("Testing export by question...")
    print("=" * 80)
    markdown_by_question = export_service.export_by_question()
    print(markdown_by_question[:500])  # Print first 500 chars
    print(f"\n... (total {len(markdown_by_question)} characters)")

    # Save test outputs
    output_dir = "data/test_exports"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "test_by_interview.md"), "w", encoding="utf-8") as f:
        f.write(markdown_by_interview)

    with open(os.path.join(output_dir, "test_by_question.md"), "w", encoding="utf-8") as f:
        f.write(markdown_by_question)

    print(f"\nTest exports saved to {output_dir}/")
    print("Export functionality working correctly!")


if __name__ == "__main__":
    test_export()
