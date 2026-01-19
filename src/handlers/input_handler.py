"""Input handler for processing different input types."""

import os
from pathlib import Path
from typing import Tuple

from src.utils.llm_client import SiliconFlowClient


class InputHandler:
    """Handler for processing different types of input (text, image)."""

    def __init__(self, client: SiliconFlowClient):
        """Initialize the input handler.

        Args:
            client: SiliconFlow API client
        """
        self.client = client

    def process_input(self, input_data: str) -> Tuple[str, str]:
        """Process input and return text content and source type.

        Args:
            input_data: Input string (either text content or path to image file)

        Returns:
            Tuple of (text_content, source_type)
            source_type can be: "text" or "image"
        """
        # Check if input is a file path to an image
        if self._is_image_file(input_data):
            text_content = self._process_image(input_data)
            return text_content, "image"
        else:
            # Treat as direct text input
            return input_data, "text"

    def _is_image_file(self, input_data: str) -> bool:
        """Check if input is a valid image file path.

        Args:
            input_data: Input string

        Returns:
            True if input is a valid image file path
        """
        # Check if it's a file path
        if not os.path.exists(input_data):
            return False

        # Check if it's an image file by extension
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
        file_path = Path(input_data)

        return file_path.suffix.lower() in image_extensions

    def _process_image(self, image_path: str) -> str:
        """Process image using OCR.

        Args:
            image_path: Path to image file

        Returns:
            Extracted text from image
        """
        ocr_prompt = """请识别这张图片中的所有文字内容，并按原样输出。
这是一张面经（面试经验分享）的截图，请提取其中的所有文字信息。
注意保持原有的格式和结构。"""

        extracted_text = self.client.process_image(image_path, ocr_prompt)
        return extracted_text
