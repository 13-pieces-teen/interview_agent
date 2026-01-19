"""SiliconFlow API client."""

from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI
from PIL import Image

from src.utils.config import Config


class SiliconFlowClient:
    """Client for interacting with SiliconFlow API."""

    def __init__(self, config: Config):
        """Initialize the client.

        Args:
            config: Application configuration
        """
        self.config = config

        # Initialize DeepSeek model for text processing
        self.deepseek_llm = ChatOpenAI(
            model=config.deepseek_model,
            openai_api_key=config.siliconflow_api_key,
            openai_api_base=config.siliconflow_api_base,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

        # Initialize GLM Vision model for image processing
        self.glm_vision_llm = ChatOpenAI(
            model=config.glm_vision_model,
            openai_api_key=config.siliconflow_api_key,
            openai_api_base=config.siliconflow_api_base,
            temperature=0.1,  # Lower temperature for OCR tasks
            max_tokens=4096,
        )

    def process_text(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> str:
        """Process text using DeepSeek model.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Model response
        """
        messages: List[Dict[str, Any]] = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.deepseek_llm.invoke(messages)
        return response.content

    def process_image(self, image_path: str, prompt: str) -> str:
        """Process image using GLM Vision model for OCR.

        Args:
            image_path: Path to the image file
            prompt: Prompt for image processing

        Returns:
            Extracted text from image
        """
        # Verify image exists
        try:
            Image.open(image_path).verify()
        except Exception as e:
            raise ValueError(f"Invalid image file: {image_path}") from e

        # Create message with image
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"file://{image_path}"},
                    },
                ],
            }
        ]

        response = self.glm_vision_llm.invoke(messages)
        return response.content

    def get_deepseek_llm(self) -> ChatOpenAI:
        """Get the DeepSeek LLM instance.

        Returns:
            ChatOpenAI instance
        """
        return self.deepseek_llm

    def get_glm_vision_llm(self) -> ChatOpenAI:
        """Get the GLM Vision LLM instance.

        Returns:
            ChatOpenAI instance
        """
        return self.glm_vision_llm
