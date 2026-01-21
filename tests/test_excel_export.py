"""Test Excel export functionality."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.database import Database
from src.services.export_service import ExportService


def test_excel_export():
    """Test Excel export functionality."""
    print("Testing Excel export...")

    # Initialize database and export service
    db = Database()
    export_service = ExportService(db)

    # Export questions to Excel
    try:
        excel_content = export_service.export_questions_to_excel()

        # Save to file for verification
        output_dir = "data/test_exports"
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "test_questions_export.xlsx")
        with open(output_file, 'wb') as f:
            f.write(excel_content)

        print(f"Excel export successful!")
        print(f"  File saved to: {output_file}")
        print(f"  File size: {len(excel_content)} bytes")

        return True
    except Exception as e:
        print(f"Excel export failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_excel_export()
    sys.exit(0 if success else 1)
