"""Exporter for saving interview experiences."""

import json
from pathlib import Path
from typing import Optional

from src.models.schema import InterviewExperience


class Exporter:
    """Exporter for saving interview experiences to various formats."""

    def __init__(self, output_dir: Path):
        """Initialize the exporter.

        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_json(
        self, experience: InterviewExperience, filename: Optional[str] = None
    ) -> Path:
        """Export interview experience to JSON file.

        Args:
            experience: InterviewExperience object
            filename: Optional custom filename (without extension)

        Returns:
            Path to saved JSON file
        """
        if filename is None:
            filename = f"interview_{experience.id}"

        filepath = self.output_dir / f"{filename}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(experience.model_dump(), f, ensure_ascii=False, indent=2, default=str)

        return filepath

    def export_markdown(
        self, experience: InterviewExperience, filename: Optional[str] = None
    ) -> Path:
        """Export interview experience to Markdown file.

        Args:
            experience: InterviewExperience object
            filename: Optional custom filename (without extension)

        Returns:
            Path to saved Markdown file
        """
        if filename is None:
            filename = f"interview_{experience.id}"

        filepath = self.output_dir / f"{filename}.md"

        markdown_content = self._generate_markdown(experience)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        return filepath

    def _generate_markdown(self, experience: InterviewExperience) -> str:
        """Generate Markdown content from InterviewExperience.

        Args:
            experience: InterviewExperience object

        Returns:
            Markdown formatted string
        """
        lines = []

        # Title
        title_parts = []
        if experience.company_name:
            title_parts.append(experience.company_name)
        if experience.position:
            title_parts.append(experience.position)
        if experience.interview_stage:
            title_parts.append(experience.interview_stage)

        if title_parts:
            lines.append(f"# {' - '.join(title_parts)}")
        else:
            lines.append("# 面经记录")

        lines.append("")

        # Metadata
        lines.append("## 基本信息")
        lines.append("")

        if experience.company_name:
            lines.append(f"- **公司**: {experience.company_name}")
        if experience.company_scale:
            lines.append(f"- **规模**: {experience.company_scale}")
        if experience.position:
            lines.append(f"- **职位**: {experience.position}")
        if experience.interview_stage:
            lines.append(f"- **轮次**: {experience.interview_stage}")
        if experience.interview_experience:
            stars = "⭐" * experience.interview_experience
            lines.append(f"- **体验**: {stars}")

        lines.append(f"- **记录时间**: {experience.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **来源**: {experience.source_type}")
        lines.append("")

        # Tags
        if experience.tags:
            lines.append("## 技术标签")
            lines.append("")
            lines.append(" | ".join([f"`{tag}`" for tag in experience.tags]))
            lines.append("")

        # Questions
        lines.append("## 面试题目")
        lines.append("")

        for idx, question in enumerate(experience.questions, 1):
            lines.append(f"### {idx}. {question.question}")
            lines.append("")

            # Question tags
            if question.tags:
                lines.append(f"**标签**: {' | '.join([f'`{tag}`' for tag in question.tags])}")
                lines.append("")

            # Answer
            if question.answer:
                lines.append("**回答**:")
                lines.append("")
                lines.append(question.answer)
                lines.append("")
                if question.has_original_answer:
                    lines.append("*（原文回答）*")
                else:
                    lines.append("*（AI生成回答）*")
            else:
                lines.append("**回答**: 暂无")

            lines.append("")
            lines.append("---")
            lines.append("")

        # Raw content (optional, commented out)
        lines.append("## 原始内容")
        lines.append("")
        lines.append("```")
        lines.append(experience.raw_content)
        lines.append("```")

        return "\n".join(lines)
