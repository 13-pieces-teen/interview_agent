"""Feishu (Lark) document exporter for interview experiences."""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime

import httpx

from src.models.schema import InterviewExperience, Question


class FeishuExporter:
    """Exporter for uploading interview experiences to Feishu documents."""

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        api_base: str = "https://open.feishu.cn/open-apis"
    ):
        """Initialize Feishu exporter.

        Args:
            app_id: Feishu app ID
            app_secret: Feishu app secret
            api_base: Feishu API base URL (default: China endpoint)
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.api_base = api_base.rstrip("/")
        self._tenant_access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    def _get_tenant_access_token(self) -> str:
        """Get tenant access token (cached).

        Returns:
            Tenant access token

        Raises:
            Exception: If failed to get token
        """
        # Check if token is still valid
        if (
            self._tenant_access_token
            and self._token_expires_at
            and datetime.now() < datetime.fromtimestamp(self._token_expires_at)
        ):
            return self._tenant_access_token

        # Request new token
        url = f"{self.api_base}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            if data.get("code") != 0:
                raise Exception(f"Failed to get access token: {data.get('msg')}")

            self._tenant_access_token = data["tenant_access_token"]
            # Token expires in 2 hours, refresh 5 minutes before expiry
            expires_in = data.get("expire", 7200) - 300
            import time
            self._token_expires_at = time.time() + expires_in

            return self._tenant_access_token

    def _create_document(self, title: str, folder_token: Optional[str] = None) -> str:
        """Create a new Feishu document.

        Args:
            title: Document title
            folder_token: Optional folder token to place document in

        Returns:
            Document token

        Raises:
            Exception: If failed to create document
        """
        token = self._get_tenant_access_token()
        url = f"{self.api_base}/docx/v1/documents"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        payload: Dict[str, Any] = {
            "title": title
        }

        if folder_token:
            payload["folder_token"] = folder_token

        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            if data.get("code") != 0:
                raise Exception(f"Failed to create document: {data.get('msg')}")

            return data["data"]["document"]["document_id"]

    def _build_document_blocks(self, experience: InterviewExperience) -> List[Dict]:
        """Build document blocks from interview experience.

        Args:
            experience: Interview experience data

        Returns:
            List of document blocks for Feishu API
        """
        blocks = []

        # Title
        title_parts = []
        if experience.company_name:
            title_parts.append(experience.company_name)
        if experience.position:
            title_parts.append(experience.position)
        if experience.interview_stage:
            title_parts.append(experience.interview_stage)

        title = " - ".join(title_parts) if title_parts else "面经记录"

        blocks.append({
            "block_type": 2,
            "text": {
                "style": {},
                "elements": [{
                    "text_run": {
                        "content": title,
                        "text_element_style": {
                            "bold": True
                        }
                    }
                }]
            }
        })

        # Basic information section
        blocks.append({
            "block_type": 2,
            "text": {
                "style": {},
                "elements": [{
                    "text_run": {
                        "content": "\n基本信息",
                        "text_element_style": {
                            "bold": True
                        }
                    }
                }]
            }
        })

        info_lines = []
        if experience.company_name:
            info_lines.append(f"公司: {experience.company_name}")
        if experience.company_scale:
            info_lines.append(f"规模: {experience.company_scale}")
        if experience.position:
            info_lines.append(f"职位: {experience.position}")
        if experience.interview_stage:
            info_lines.append(f"轮次: {experience.interview_stage}")
        if experience.interview_experience:
            info_lines.append(f"体验: {experience.interview_experience}")

        info_lines.append(f"记录时间: {experience.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        info_lines.append(f"来源: {experience.source_type}")

        # Combine info lines into one block to avoid too many blocks
        info_text = "\n".join(f"• {line}" for line in info_lines)
        blocks.append({
            "block_type": 2,
            "text": {
                "style": {},
                "elements": [{
                    "text_run": {
                        "content": info_text
                    }
                }]
            }
        })

        # Tags section
        if experience.tags:
            blocks.append({
                "block_type": 2,
                "text": {
                    "style": {},
                    "elements": [{
                        "text_run": {
                            "content": "\n技术标签",
                            "text_element_style": {
                                "bold": True
                            }
                        }
                    }]
                }
            })

            tags_text = " | ".join(experience.tags)
            blocks.append({
                "block_type": 2,
                "text": {
                    "style": {},
                    "elements": [{
                        "text_run": {
                            "content": tags_text
                        }
                    }]
                }
            })

        # Questions section
        blocks.append({
            "block_type": 2,
            "text": {
                "style": {},
                "elements": [{
                    "text_run": {
                        "content": "\n面试题目",
                        "text_element_style": {
                            "bold": True
                        }
                    }
                }]
            }
        })

        for idx, question in enumerate(experience.questions, 1):
            # Question heading
            blocks.append({
                "block_type": 2,
                "text": {
                    "style": {},
                    "elements": [{
                        "text_run": {
                            "content": f"\n{idx}. {question.question}",
                            "text_element_style": {
                                "bold": True
                            }
                        }
                    }]
                }
            })

            # Question tags
            if question.tags:
                tags_str = " | ".join(question.tags)
                blocks.append({
                    "block_type": 2,
                    "text": {
                        "style": {},
                        "elements": [{
                            "text_run": {
                                "content": f"标签: {tags_str}"
                            }
                        }]
                    }
                })

            # Answer
            if question.answer:
                answer_note = "(原文回答)" if question.has_original_answer else "(AI生成回答)"
                answer_content = f"回答: {question.answer}\n{answer_note}"
                blocks.append({
                    "block_type": 2,
                    "text": {
                        "style": {},
                        "elements": [{
                            "text_run": {
                                "content": answer_content
                            }
                        }]
                    }
                })
            else:
                blocks.append({
                    "block_type": 2,
                    "text": {
                        "style": {},
                        "elements": [{
                            "text_run": {
                                "content": "回答: 暂无"
                            }
                        }]
                    }
                })

        # Raw content section
        if experience.raw_content and experience.raw_content.strip():
            blocks.append({
                "block_type": 2,
                "text": {
                    "style": {},
                    "elements": [{
                        "text_run": {
                            "content": "\n原始内容",
                            "text_element_style": {
                                "bold": True
                            }
                        }
                    }]
                }
            })

            # Split raw content into chunks if too long
            max_length = 3000
            raw_content = experience.raw_content
            if len(raw_content) > max_length:
                raw_content = raw_content[:max_length] + "\n... (内容已截断)"

            blocks.append({
                "block_type": 2,
                "text": {
                    "style": {},
                    "elements": [{
                        "text_run": {
                            "content": raw_content
                        }
                    }]
                }
            })

        return blocks

    def _add_blocks_to_document(
        self,
        document_id: str,
        blocks: List[Dict],
        parent_id: Optional[str] = None
    ) -> bool:
        """Add blocks to a Feishu document.

        Args:
            document_id: Document ID
            blocks: List of blocks to add
            parent_id: Optional parent block ID (None for root)

        Returns:
            True if successful

        Raises:
            Exception: If failed to add blocks
        """
        token = self._get_tenant_access_token()
        # IMPORTANT: Add document_revision_id=-1 for latest revision
        url = f"{self.api_base}/docx/v1/documents/{document_id}/blocks/{parent_id or 'root'}/children?document_revision_id=-1"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        # Batch insert blocks (max 50 per request)
        batch_size = 50
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]

            # Add style field to all text blocks
            for block in batch:
                if block.get("block_type") == 2 and "text" in block:
                    if "style" not in block["text"]:
                        block["text"]["style"] = {}

            payload = {
                "children": batch,
                "index": -1  # Append to end
            }

            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()

                data = response.json()
                if data.get("code") != 0:
                    raise Exception(f"Failed to add blocks: {data.get('msg')}")

        return True

    def export_to_feishu(
        self,
        experience: InterviewExperience,
        folder_token: Optional[str] = None
    ) -> Dict[str, str]:
        """Export interview experience to Feishu document.

        Args:
            experience: Interview experience to export
            folder_token: Optional folder token to place document in

        Returns:
            Dictionary with document_id and document_url

        Raises:
            Exception: If export fails
        """
        # Build title
        title_parts = []
        if experience.company_name:
            title_parts.append(experience.company_name)
        if experience.position:
            title_parts.append(experience.position)
        if experience.interview_stage:
            title_parts.append(experience.interview_stage)

        title = " - ".join(title_parts) if title_parts else "面经记录"
        title = f"[面经] {title} - {experience.created_at.strftime('%Y-%m-%d')}"

        # Create document
        document_id = self._create_document(title, folder_token)

        # Build and add content blocks
        blocks = self._build_document_blocks(experience)
        self._add_blocks_to_document(document_id, blocks)

        # Build document URL
        document_url = f"https://feishu.cn/docx/{document_id}"

        return {
            "document_id": document_id,
            "document_url": document_url,
            "title": title
        }

    def export_multiple_to_feishu(
        self,
        experiences: List[InterviewExperience],
        folder_token: Optional[str] = None,
        create_index: bool = True
    ) -> Dict[str, Any]:
        """Export multiple interview experiences to Feishu.

        Args:
            experiences: List of interview experiences
            folder_token: Optional folder token
            create_index: Whether to create an index document

        Returns:
            Dictionary with export results

        Raises:
            Exception: If export fails
        """
        results = []

        for exp in experiences:
            try:
                result = self.export_to_feishu(exp, folder_token)
                results.append({
                    "success": True,
                    "experience_id": exp.id,
                    "document_id": result["document_id"],
                    "document_url": result["document_url"],
                    "title": result["title"]
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "experience_id": exp.id,
                    "error": str(e)
                })

        # Create index document if requested
        index_doc = None
        if create_index and results:
            try:
                index_doc = self._create_index_document(results, folder_token)
            except Exception as e:
                print(f"Warning: Failed to create index document: {e}")

        return {
            "total": len(experiences),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results,
            "index_document": index_doc
        }

    def _create_index_document(
        self,
        results: List[Dict],
        folder_token: Optional[str] = None
    ) -> Dict[str, str]:
        """Create an index document with links to all exported documents.

        Args:
            results: Export results
            folder_token: Optional folder token

        Returns:
            Dictionary with index document info
        """
        title = f"面经索引 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        document_id = self._create_document(title, folder_token)

        blocks = [
            {
                "block_type": 2,
                "text": {
                    "style": {},
                    "elements": [{
                        "text_run": {
                            "content": "面经导出索引",
                            "text_element_style": {
                                "bold": True
                            }
                        }
                    }]
                }
            },
            {
                "block_type": 2,
                "text": {
                    "style": {},
                    "elements": [{
                        "text_run": {
                            "content": f"\n导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    }]
                }
            },
            {
                "block_type": 2,
                "text": {
                    "style": {},
                    "elements": [{
                        "text_run": {
                            "content": f"总计: {len(results)} 条面经\n"
                        }
                    }]
                }
            }
        ]

        # Add links to each document
        for idx, result in enumerate(results, 1):
            if result["success"]:
                blocks.append({
                    "block_type": 2,
                    "text": {
                        "style": {},
                        "elements": [
                            {
                                "text_run": {
                                    "content": f"{idx}. "
                                }
                            },
                            {
                                "text_run": {
                                    "content": result["title"],
                                    "text_element_style": {
                                        "link": {
                                            "url": result["document_url"]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                })
            else:
                blocks.append({
                    "block_type": 2,
                    "text": {
                        "style": {},
                        "elements": [{
                            "text_run": {
                                "content": f"{idx}. 导出失败: {result.get('error', 'Unknown error')}"
                            }
                        }]
                    }
                })

        self._add_blocks_to_document(document_id, blocks)

        return {
            "document_id": document_id,
            "document_url": f"https://feishu.cn/docx/{document_id}",
            "title": title
        }

    def test_connection(self) -> bool:
        """Test connection to Feishu API.

        Returns:
            True if connection successful

        Raises:
            Exception: If connection fails
        """
        try:
            self._get_tenant_access_token()
            return True
        except Exception as e:
            raise Exception(f"Failed to connect to Feishu API: {str(e)}")
