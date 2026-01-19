"""Configuration management for Interview Agent."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Config(BaseModel):
    """Application configuration."""

    # API Configuration
    siliconflow_api_key: str = Field(..., description="SiliconFlow API key")
    siliconflow_api_base: str = Field(
        default="https://api.siliconflow.cn/v1", description="SiliconFlow API base URL"
    )

    # Model Configuration
    deepseek_model: str = Field(
        default="Pro/deepseek-ai/DeepSeek-V3.2", description="DeepSeek model name"
    )
    glm_vision_model: str = Field(
        default="zai-org/GLM-4.6V", description="GLM Vision model name"
    )

    # Directory Configuration
    output_dir: Path = Field(default=Path("output"), description="Output directory")
    data_dir: Path = Field(default=Path("data"), description="Data directory")

    # Processing Configuration
    generate_missing_answers: bool = Field(
        default=False, description="Whether to generate missing answers"
    )
    max_tokens: int = Field(default=4096, description="Max tokens for LLM generation")
    temperature: float = Field(default=0.7, description="Temperature for LLM generation")

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Config":
        """Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file

        Returns:
            Config instance
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        return cls(
            siliconflow_api_key=os.getenv("SILICONFLOW_API_KEY", ""),
            siliconflow_api_base=os.getenv(
                "SILICONFLOW_API_BASE", "https://api.siliconflow.cn/v1"
            ),
            deepseek_model=os.getenv("DEEPSEEK_MODEL", "Pro/deepseek-ai/DeepSeek-V3.2"),
            glm_vision_model=os.getenv("GLM_VISION_MODEL", "zai-org/GLM-4.6V"),
            output_dir=Path(os.getenv("OUTPUT_DIR", "output")),
            data_dir=Path(os.getenv("DATA_DIR", "data")),
        )

    def ensure_directories(self) -> None:
        """Ensure output and data directories exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
