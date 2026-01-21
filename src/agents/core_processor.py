"""Core Processor Agent for processing interview experiences."""

import json
from typing import Dict, Any

from src.models.schema import InterviewExperience, Question
from src.prompts.core_processor_prompt import (
    CORE_PROCESSOR_SYSTEM_PROMPT,
    get_user_prompt,
)
from src.utils.llm_client import SiliconFlowClient


class CoreProcessorAgent:
    """Agent for processing interview experience content.

    This agent handles:
    - Structured parsing of interview content
    - Content cleaning (removing irrelevant information)
    - Tag classification
    - Answer enhancement (if enabled)
    """

    def __init__(self, client: SiliconFlowClient):
        """Initialize the agent.

        Args:
            client: SiliconFlow API client
        """
        self.client = client

    def process(
        self, raw_content: str, source_type: str
    ) -> InterviewExperience:
        """Process raw interview experience content.

        Args:
            raw_content: Raw interview experience text
            source_type: Source type (text or image)

        Returns:
            Processed InterviewExperience object

        Raises:
            ValueError: If LLM response cannot be parsed or has invalid structure
        """
        # Generate prompt (always without answer generation)
        user_prompt = get_user_prompt(raw_content, generate_answers=False)

        # Call LLM
        response = self.client.process_text(
            prompt=user_prompt, system_prompt=CORE_PROCESSOR_SYSTEM_PROMPT
        )

        # Parse JSON response
        try:
            parsed_data = self._parse_response(response)
        except ValueError as e:
            # This is a real JSON parsing error
            raise ValueError(f"LLM返回的不是有效JSON格式: {str(e)}")

        # Convert to InterviewExperience object
        try:
            experience = self._build_experience(parsed_data, raw_content, source_type)
        except (KeyError, ValueError, TypeError) as e:
            # This is a validation/structure error
            raise ValueError(f"LLM返回的数据结构不完整或格式错误: {str(e)}\n请稍后重试或使用不同的内容。")

        return experience

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to JSON.

        Args:
            response: LLM response string

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If response is not valid JSON
        """
        # Remove potential markdown code blocks
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败 - {str(e)}")

    def _build_experience(
        self, parsed_data: Dict[str, Any], raw_content: str, source_type: str
    ) -> InterviewExperience:
        """Build InterviewExperience object from parsed data.

        Args:
            parsed_data: Parsed JSON data
            raw_content: Original raw content
            source_type: Source type

        Returns:
            InterviewExperience object
        """
        # Build questions list
        questions = []
        for q_data in parsed_data.get("questions", []):
            question = Question(
                question=q_data["question"],
                answer=q_data.get("answer"),
                has_original_answer=q_data.get("has_original_answer", False),
                tags=q_data.get("tags", []),
            )
            questions.append(question)

        # Build InterviewExperience
        experience = InterviewExperience(
            source_type=source_type,
            company_name=parsed_data.get("company_name"),
            company_scale=parsed_data.get("company_scale"),
            position=parsed_data.get("position"),
            interview_stage=parsed_data.get("interview_stage"),
            interview_experience=parsed_data.get("interview_experience"),
            questions=questions,
            tags=parsed_data.get("tags", []),
            raw_content=raw_content,
        )

        return experience
