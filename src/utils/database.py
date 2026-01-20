"""Database utilities for storing interview experiences."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from src.models.schema import InterviewExperience


class Database:
    """SQLite database handler for interview experiences."""

    def __init__(self, db_path: str = "data/interviews.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS experiences (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    company_name TEXT,
                    company_scale TEXT,
                    position TEXT,
                    interview_stage TEXT,
                    interview_experience TEXT,
                    questions_json TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    raw_content TEXT NOT NULL,
                    questions_count INTEGER DEFAULT 0,
                    has_answers BOOLEAN DEFAULT FALSE,
                    processing_time REAL DEFAULT 0
                )
            """
            )

            # Migration: Add processing_time column if it doesn't exist
            cursor = conn.execute("PRAGMA table_info(experiences)")
            columns = [row[1] for row in cursor.fetchall()]
            if "processing_time" not in columns:
                conn.execute(
                    """
                    ALTER TABLE experiences
                    ADD COLUMN processing_time REAL DEFAULT 0
                """
                )

            # Create indexes for faster queries
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON experiences(created_at DESC)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_company_name
                ON experiences(company_name)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_company_scale
                ON experiences(company_scale)
            """
            )

    def save_experience(self, experience: InterviewExperience, processing_time: float = 0) -> str:
        """
        Save an interview experience to database.

        Args:
            experience: InterviewExperience object to save
            processing_time: Time taken to process in seconds

        Returns:
            ID of the saved experience
        """
        with self._get_connection() as conn:
            # Check if questions have answers
            has_answers = any(q.answer for q in experience.questions)

            conn.execute(
                """
                INSERT OR REPLACE INTO experiences (
                    id, created_at, source_type, company_name, company_scale,
                    position, interview_stage, interview_experience,
                    questions_json, tags_json, raw_content,
                    questions_count, has_answers, processing_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    experience.id,
                    experience.created_at.isoformat(),
                    experience.source_type,
                    experience.company_name,
                    experience.company_scale,
                    experience.position,
                    experience.interview_stage,
                    experience.interview_experience,
                    json.dumps([q.model_dump() for q in experience.questions]),
                    json.dumps(experience.tags),
                    experience.raw_content,
                    len(experience.questions),
                    has_answers,
                    processing_time,
                ),
            )

        return experience.id

    def get_experience(self, experience_id: str) -> Optional[InterviewExperience]:
        """
        Get an interview experience by ID.

        Args:
            experience_id: ID of the experience to retrieve

        Returns:
            InterviewExperience object or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM experiences WHERE id = ?
            """,
                (experience_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_experience(row)

    def list_experiences(
        self,
        company_name: Optional[str] = None,
        company_scale: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interview_stage: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List interview experiences with optional filtering.

        Args:
            company_name: Filter by company name (partial match)
            company_scale: Filter by company scale
            tags: Filter by tags (any match)
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            interview_stage: Filter by interview stage
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of experience dictionaries (lightweight, without full questions)
        """
        query = """
            SELECT
                id, created_at, source_type, company_name, company_scale,
                position, interview_stage, interview_experience,
                tags_json, questions_count, has_answers, processing_time
            FROM experiences
            WHERE 1=1
        """
        params = []

        if company_name:
            query += " AND company_name LIKE ?"
            params.append(f"%{company_name}%")

        if company_scale:
            query += " AND company_scale = ?"
            params.append(company_scale)

        if interview_stage:
            query += " AND interview_stage = ?"
            params.append(interview_stage)

        if start_date:
            query += " AND created_at >= ?"
            params.append(start_date)

        if end_date:
            query += " AND created_at <= ?"
            params.append(end_date)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        results = []
        for row in rows:
            exp_dict = dict(row)
            exp_dict["tags"] = json.loads(exp_dict.pop("tags_json"))
            # Convert SQLite integer boolean to Python boolean
            exp_dict["has_answers"] = bool(exp_dict["has_answers"])

            # Filter by tags if specified
            if tags:
                if not any(tag in exp_dict["tags"] for tag in tags):
                    continue

            results.append(exp_dict)

        return results

    def delete_experience(self, experience_id: str) -> bool:
        """
        Delete an interview experience by ID.

        Args:
            experience_id: ID of the experience to delete

        Returns:
            True if deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                DELETE FROM experiences WHERE id = ?
            """,
                (experience_id,),
            )
            return cursor.rowcount > 0

    def get_all_tags(self) -> List[str]:
        """
        Get all unique tags from all experiences.

        Returns:
            List of unique tags sorted by frequency
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT tags_json FROM experiences")
            rows = cursor.fetchall()

        tag_count: Dict[str, int] = {}
        for row in rows:
            tags = json.loads(row["tags_json"])
            for tag in tags:
                tag_count[tag] = tag_count.get(tag, 0) + 1

        # Sort by frequency (descending)
        sorted_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, _ in sorted_tags]

    def get_all_companies(self) -> List[str]:
        """
        Get all unique company names.

        Returns:
            List of unique company names
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT DISTINCT company_name
                FROM experiences
                WHERE company_name IS NOT NULL
                ORDER BY company_name
            """
            )
            rows = cursor.fetchall()

        return [row["company_name"] for row in rows]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with statistics
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total_experiences,
                    SUM(questions_count) as total_questions,
                    COUNT(DISTINCT company_name) as unique_companies
                FROM experiences
            """
            )
            row = cursor.fetchone()

        return dict(row)

    def _row_to_experience(self, row: sqlite3.Row) -> InterviewExperience:
        """Convert database row to InterviewExperience object."""
        from src.models.schema import Question

        questions_data = json.loads(row["questions_json"])
        questions = [Question(**q) for q in questions_data]

        return InterviewExperience(
            id=row["id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            source_type=row["source_type"],
            company_name=row["company_name"],
            company_scale=row["company_scale"],
            position=row["position"],
            interview_stage=row["interview_stage"],
            interview_experience=row["interview_experience"],
            questions=questions,
            tags=json.loads(row["tags_json"]),
            raw_content=row["raw_content"],
            processing_time=row["processing_time"] if "processing_time" in row.keys() else 0,
        )

    def get_grouped_questions(
        self,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        company_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get questions grouped by question text.

        Args:
            search: Search query for question text
            tags: Filter by tags
            company_name: Filter by company name
            limit: Maximum number of groups to return
            offset: Offset for pagination

        Returns:
            List of question groups with occurrences
        """
        with self._get_connection() as conn:
            # Get all experiences
            cursor = conn.execute(
                """
                SELECT id, created_at, company_name, position, interview_stage, questions_json
                FROM experiences
                ORDER BY created_at DESC
            """
            )
            rows = cursor.fetchall()

        # Group questions
        question_groups: Dict[str, Dict[str, Any]] = {}

        for row in rows:
            exp_id = row["id"]
            exp_company = row["company_name"]
            exp_position = row["position"]
            exp_stage = row["interview_stage"]
            exp_created_at = row["created_at"]
            questions_data = json.loads(row["questions_json"])

            # Apply company filter
            if company_name and (not exp_company or company_name.lower() not in exp_company.lower()):
                continue

            for q in questions_data:
                question_text = q["question"].strip()

                # Apply search filter
                if search and search.lower() not in question_text.lower():
                    continue

                # Apply tags filter
                q_tags = q.get("tags", [])
                if tags and not any(tag in q_tags for tag in tags):
                    continue

                # Add to group
                if question_text not in question_groups:
                    question_groups[question_text] = {
                        "question": question_text,
                        "count": 0,
                        "tags": set(),
                        "occurrences": [],
                    }

                question_groups[question_text]["count"] += 1
                question_groups[question_text]["tags"].update(q_tags)
                question_groups[question_text]["occurrences"].append({
                    "experience_id": exp_id,
                    "company_name": exp_company,
                    "position": exp_position,
                    "interview_stage": exp_stage,
                    "answer": q.get("answer"),
                    "has_original_answer": q.get("has_original_answer", False),
                    "created_at": exp_created_at,
                })

        # Convert to list and sort by count
        groups = []
        for group in question_groups.values():
            group["tags"] = sorted(list(group["tags"]))
            groups.append(group)

        groups.sort(key=lambda x: x["count"], reverse=True)

        # Apply pagination
        total = len(groups)
        groups = groups[offset:offset + limit]

        return groups
