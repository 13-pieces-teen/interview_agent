"""FastAPI application for interview agent."""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from threading import Thread
import os
import time
import uuid
from datetime import datetime

from src.main import InterviewAgent
from src.utils.config import Config
from src.models.schema import InterviewExperience
from src.utils.database import Database
from src.validators.content_validator import validate_content

# Initialize FastAPI app
app = FastAPI(
    title="Interview Agent API",
    description="AI-powered interview experience processor",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load config and initialize agent
config = Config.from_env()
agent = InterviewAgent(config)
db = Database()


# Request/Response models
class ProcessTextRequest(BaseModel):
    """Request model for processing text."""

    content: str
    generate_answers: bool = False
    export_format: str = "both"  # "json", "markdown", or "both"


class ProcessResponse(BaseModel):
    """Response model for processing results."""

    success: bool
    processing_time: float
    experience: Optional[dict] = None
    experience_id: Optional[str] = None  # Added for saved experience ID
    output_files: List[str] = []
    error: Optional[str] = None
    validation_score: Optional[int] = None  # Content validation score
    validation_message: Optional[str] = None  # Validation message


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str
    version: str


class ValidationRequest(BaseModel):
    """Request model for content validation."""

    content: str


class ValidationResponse(BaseModel):
    """Response model for content validation."""

    is_valid: bool
    confidence_score: int
    message: str


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0",
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0",
    )


@app.post("/api/validate", response_model=ValidationResponse)
async def validate_text(request: ValidationRequest):
    """
    Validate if content is interview experience related.

    Args:
        request: Request containing content to validate

    Returns:
        ValidationResponse with validation results
    """
    try:
        is_valid, confidence_score, message = validate_content(request.content)

        return ValidationResponse(
            is_valid=is_valid,
            confidence_score=confidence_score,
            message=message,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process/text", response_model=ProcessResponse)
async def process_text(request: ProcessTextRequest):
    """
    Process interview experience from text content.

    Args:
        request: Request containing text content and processing options

    Returns:
        ProcessResponse with results and output files
    """
    try:
        start_time = time.time()

        # Validate content first
        is_valid, validation_score, validation_message = validate_content(request.content)

        if not is_valid:
            processing_time = time.time() - start_time
            return ProcessResponse(
                success=False,
                processing_time=processing_time,
                error=validation_message,
                validation_score=validation_score,
                validation_message=validation_message,
            )

        # Process the interview experience
        result = agent.process(
            input_data=request.content,
            export_format=request.export_format,
        )

        processing_time = time.time() - start_time

        if result.success:
            # Auto-save to database
            experience_id = None
            if result.experience:
                experience_id = db.save_experience(result.experience, processing_time)

            return ProcessResponse(
                success=True,
                processing_time=processing_time,
                experience=result.experience.model_dump() if result.experience else None,
                experience_id=experience_id,
                output_files=result.output_files,
                validation_score=validation_score,
                validation_message=validation_message,
            )
        else:
            return ProcessResponse(
                success=False,
                processing_time=processing_time,
                error=result.error,
                validation_score=validation_score,
                validation_message=validation_message,
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process/images", response_model=ProcessResponse)
async def process_images(
    files: List[UploadFile] = File(...),
    generate_answers: bool = Form(False),
    export_format: str = Form("both"),
):
    """
    Process interview experience from multiple image files.

    Args:
        files: List of uploaded image files
        generate_answers: Whether to generate missing answers
        export_format: Export format (json, markdown, or both)

    Returns:
        ProcessResponse with combined results and output files
    """
    try:
        start_time = time.time()

        # Save uploaded files temporarily
        temp_dir = os.path.join(config.data_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)

        temp_file_paths = []
        combined_text = []

        # Process each image to extract text
        for idx, file in enumerate(files):
            temp_file_path = os.path.join(
                temp_dir, f"temp_{int(time.time())}_{idx}_{file.filename}"
            )

            with open(temp_file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            temp_file_paths.append(temp_file_path)

            # Extract text from image using input handler
            try:
                text_content, _ = agent.input_handler.process_input(temp_file_path)
                combined_text.append(f"=== Image {idx + 1}: {file.filename} ===\n{text_content}")
            except Exception as e:
                combined_text.append(f"=== Image {idx + 1}: {file.filename} ===\nError: {str(e)}")

        # Combine all extracted text
        full_text = "\n\n".join(combined_text)

        try:
            # Process the combined text
            result = agent.process(
                input_data=full_text,
                export_format=export_format,
            )

            processing_time = time.time() - start_time

            if result.success:
                return ProcessResponse(
                    success=True,
                    processing_time=processing_time,
                    experience=result.experience.model_dump() if result.experience else None,
                    output_files=result.output_files,
                )
            else:
                return ProcessResponse(
                    success=False,
                    processing_time=processing_time,
                    error=result.error,
                )

        finally:
            # Clean up temp files
            for temp_file_path in temp_file_paths:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process/image", response_model=ProcessResponse)
async def process_image(
    file: UploadFile = File(...),
    generate_answers: bool = Form(False),
    export_format: str = Form("both"),
):
    """
    Process interview experience from image file.

    Args:
        file: Uploaded image file
        generate_answers: Whether to generate missing answers
        export_format: Export format (json, markdown, or both)

    Returns:
        ProcessResponse with results and output files
    """
    try:
        start_time = time.time()

        # Save uploaded file temporarily
        temp_dir = os.path.join(config.data_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)

        temp_file_path = os.path.join(temp_dir, f"temp_{int(time.time())}_{file.filename}")

        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        try:
            # Process the image
            result = agent.process(
                input_data=temp_file_path,
                export_format=export_format,
            )

            processing_time = time.time() - start_time

            if result.success:
                # Auto-save to database
                experience_id = None
                if result.experience:
                    experience_id = db.save_experience(result.experience, processing_time)

                return ProcessResponse(
                    success=True,
                    processing_time=processing_time,
                    experience=result.experience.model_dump() if result.experience else None,
                    experience_id=experience_id,
                    output_files=result.output_files,
                )
            else:
                return ProcessResponse(
                    success=False,
                    processing_time=processing_time,
                    error=result.error,
                )

        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """
    Download generated output file.

    Args:
        filename: Name of the file to download

    Returns:
        FileResponse with the requested file
    """
    file_path = os.path.join(config.output_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Determine media type based on file extension
    if filename.endswith(".json"):
        media_type = "application/json"
    elif filename.endswith(".md"):
        media_type = "text/markdown"
    else:
        media_type = "application/octet-stream"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
    )


@app.get("/api/files")
async def list_files():
    """
    List all generated output files.

    Returns:
        List of output files with metadata
    """
    try:
        output_dir = config.output_dir

        if not os.path.exists(output_dir):
            return {"files": []}

        files = []
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)

            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append(
                    {
                        "filename": filename,
                        "size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    }
                )

        # Sort by modified time (newest first)
        files.sort(key=lambda x: x["modified_at"], reverse=True)

        return {"files": files}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Database API endpoints
@app.get("/api/experiences")
async def list_experiences(
    company_name: Optional[str] = None,
    company_scale: Optional[str] = None,
    tags: Optional[str] = None,  # Comma-separated tags
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interview_stage: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    """
    List saved interview experiences with filtering and pagination.

    Args:
        company_name: Filter by company name (partial match)
        company_scale: Filter by company scale
        tags: Comma-separated tags to filter by
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        interview_stage: Filter by interview stage
        limit: Maximum number of results (default 50)
        offset: Offset for pagination (default 0)

    Returns:
        List of experiences with metadata
    """
    try:
        tag_list = [t.strip() for t in tags.split(",")] if tags else None

        experiences = db.list_experiences(
            company_name=company_name,
            company_scale=company_scale,
            tags=tag_list,
            start_date=start_date,
            end_date=end_date,
            interview_stage=interview_stage,
            limit=limit,
            offset=offset,
        )

        return {"experiences": experiences, "count": len(experiences)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/experiences/{experience_id}")
async def get_experience(experience_id: str):
    """
    Get a specific interview experience by ID.

    Args:
        experience_id: ID of the experience to retrieve

    Returns:
        Full experience data including all questions
    """
    try:
        experience = db.get_experience(experience_id)

        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")

        return {"experience": experience.model_dump()}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/experiences/{experience_id}")
async def delete_experience(experience_id: str):
    """
    Delete an interview experience by ID.

    Args:
        experience_id: ID of the experience to delete

    Returns:
        Success message
    """
    try:
        deleted = db.delete_experience(experience_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Experience not found")

        return {"success": True, "message": "Experience deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UpdateExperienceRequest(BaseModel):
    """Request model for updating experience."""

    company_name: Optional[str] = None
    company_scale: Optional[str] = None
    position: Optional[str] = None
    interview_stage: Optional[str] = None
    interview_experience: Optional[str] = None
    tags: Optional[List[str]] = None
    questions: Optional[List[dict]] = None


@app.put("/api/experiences/{experience_id}")
async def update_experience(experience_id: str, request: UpdateExperienceRequest):
    """
    Update an interview experience.

    Args:
        experience_id: ID of the experience to update
        request: Fields to update

    Returns:
        Updated experience
    """
    try:
        # Get existing experience
        experience = db.get_experience(experience_id)
        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")

        # Update fields
        if request.company_name is not None:
            experience.company_name = request.company_name
        if request.company_scale is not None:
            experience.company_scale = request.company_scale
        if request.position is not None:
            experience.position = request.position
        if request.interview_stage is not None:
            experience.interview_stage = request.interview_stage
        if request.interview_experience is not None:
            experience.interview_experience = request.interview_experience
        if request.tags is not None:
            experience.tags = request.tags
        if request.questions is not None:
            from src.models.schema import Question
            experience.questions = [Question(**q) for q in request.questions]

        # Save back to database
        db.save_experience(experience)

        return {"success": True, "experience": experience.model_dump()}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tags")
async def get_all_tags():
    """
    Get all unique tags from saved experiences.

    Returns:
        List of tags sorted by frequency
    """
    try:
        tags = db.get_all_tags()
        return {"tags": tags}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies")
async def get_all_companies():
    """
    Get all unique company names from saved experiences.

    Returns:
        List of company names
    """
    try:
        companies = db.get_all_companies()
        return {"companies": companies}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """
    Get database statistics.

    Returns:
        Statistics about saved experiences
    """
    try:
        stats = db.get_stats()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Answer generation task tracking
answer_generation_tasks: Dict[str, dict] = {}


@app.post("/api/experiences/{experience_id}/generate-answers")
async def generate_answers_async(experience_id: str):
    """
    Start async answer generation for an experience.

    This endpoint starts a background task to generate answers for questions
    that don't have answers. Returns immediately with a task ID.

    Args:
        experience_id: ID of the experience to generate answers for

    Returns:
        Task information including task_id and status
    """
    try:
        # Get experience from database
        experience = db.get_experience(experience_id)
        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")

        # Check if there are questions without answers
        questions_without_answers = [
            q for q in experience.questions if not q.answer or not q.has_original_answer
        ]

        if not questions_without_answers:
            return {
                "message": "All questions already have answers",
                "questions_count": len(experience.questions),
            }

        # Create task
        task_id = str(uuid.uuid4())
        answer_generation_tasks[task_id] = {
            "status": "pending",
            "experience_id": experience_id,
            "progress": 0,
            "total_questions": len(questions_without_answers),
            "created_at": datetime.utcnow().isoformat(),
        }

        # Start background thread
        thread = Thread(
            target=_generate_answers_background,
            args=(task_id, experience_id),
            daemon=True
        )
        thread.start()

        return {
            "task_id": task_id,
            "status": "started",
            "message": f"Answer generation started for {len(questions_without_answers)} questions",
            "total_questions": len(questions_without_answers),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _generate_answers_background(task_id: str, experience_id: str):
    """Background worker to generate answers."""
    try:
        # Update status
        answer_generation_tasks[task_id]["status"] = "processing"

        # Get experience
        experience = db.get_experience(experience_id)
        if not experience:
            answer_generation_tasks[task_id]["status"] = "failed"
            answer_generation_tasks[task_id]["error"] = "Experience not found"
            return

        # Generate answers using AnswerGeneratorAgent
        from src.agents.answer_generator import AnswerGeneratorAgent

        generator = AnswerGeneratorAgent(agent.client)
        generated_answers = generator.generate_answers(experience.questions)

        # Update questions with generated answers
        for i, answer in enumerate(generated_answers):
            if answer and not experience.questions[i].has_original_answer:
                experience.questions[i].answer = answer
                # Keep has_original_answer as False for generated answers

        # Save back to database
        db.save_experience(experience)

        # Update task status
        answer_generation_tasks[task_id]["status"] = "completed"
        answer_generation_tasks[task_id]["progress"] = len(
            [q for q in experience.questions if not q.has_original_answer and q.answer]
        )
        answer_generation_tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()

    except Exception as e:
        answer_generation_tasks[task_id]["status"] = "failed"
        answer_generation_tasks[task_id]["error"] = str(e)
        print(f"Error generating answers for task {task_id}: {e}")


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of an answer generation task.

    Args:
        task_id: Task ID returned from generate-answers endpoint

    Returns:
        Task status information
    """
    if task_id not in answer_generation_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return answer_generation_tasks[task_id]


@app.get("/api/questions/grouped")
async def get_grouped_questions(
    search: Optional[str] = None,
    tags: Optional[str] = None,
    company_name: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """
    Get questions grouped by question text with all occurrences.

    Args:
        search: Search query for question text
        tags: Comma-separated tags to filter by
        company_name: Filter by company name
        limit: Maximum number of question groups to return
        offset: Offset for pagination

    Returns:
        List of question groups with all occurrences
    """
    try:
        tag_list = [t.strip() for t in tags.split(",")] if tags else None

        groups = db.get_grouped_questions(
            search=search,
            tags=tag_list,
            company_name=company_name,
            limit=limit,
            offset=offset,
        )

        return {"total": len(groups), "groups": groups}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
