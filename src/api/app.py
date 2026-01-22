"""FastAPI application for interview agent."""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
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
from src.utils.batch_processor import batch_processor, TaskStatus
from src.utils.async_task_queue import task_queue, TaskType, Task
from src.services.export_service import ExportService

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
export_service = ExportService(db)


# Initialize async task queue
def process_task(task: Task) -> Dict:
    """通用任务处理函数"""
    try:
        if task.type == TaskType.TEXT:
            # 处理文本任务
            result = agent.process(
                input_data=task.input_data,
                export_format=task.export_format,
            )

            if result.success and result.experience:
                # 保存到数据库
                experience_id = db.save_experience(result.experience, task.processing_time)

                return {
                    "success": True,
                    "experience_id": experience_id,
                    "experience": result.experience.model_dump(),
                    "output_files": result.output_files,
                }
            else:
                return {
                    "success": False,
                    "error": result.error or "Processing failed"
                }

        elif task.type == TaskType.IMAGE:
            # 处理图片任务
            file_paths = task.input_data  # 图片文件路径列表

            try:
                combined_text = []
                for idx, file_path in enumerate(file_paths):
                    try:
                        text_content, _ = agent.input_handler.process_input(file_path)
                        combined_text.append(f"=== Image {idx + 1} ===\n{text_content}")
                    except Exception as e:
                        combined_text.append(f"=== Image {idx + 1} ===\nError: {str(e)}")

                full_text = "\n\n".join(combined_text)

                # 处理合并后的文本
                result = agent.process(
                    input_data=full_text,
                    export_format=task.export_format,
                )

                if result.success and result.experience:
                    experience_id = db.save_experience(result.experience, task.processing_time)

                    return {
                        "success": True,
                        "experience_id": experience_id,
                        "experience": result.experience.model_dump(),
                        "output_files": result.output_files,
                    }
                else:
                    return {
                        "success": False,
                        "error": result.error or "Processing failed"
                    }

            finally:
                # 清理临时文件
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        os.remove(file_path)

        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task.type}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


task_queue.set_process_function(process_task)
task_queue.start_worker()
print("✓ 异步任务队列系统已启动")


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


@app.post("/api/process/batch")
async def process_batch_upload(
    files: List[UploadFile] = File(...),
    generate_answers: bool = Form(False),
    export_format: str = Form("both"),
):
    """
    Create a batch processing task for multiple files (processed sequentially).

    Args:
        files: List of uploaded files (images or text)
        generate_answers: Whether to generate missing answers
        export_format: Export format (json, markdown, or both)

    Returns:
        Task ID and initial status
    """
    try:
        # Save uploaded files temporarily
        temp_dir = os.path.join(config.data_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)

        temp_file_paths = []
        file_names = []

        # Save all files
        for idx, file in enumerate(files):
            temp_file_path = os.path.join(
                temp_dir, f"batch_{int(time.time())}_{idx}_{file.filename}"
            )

            with open(temp_file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            temp_file_paths.append(temp_file_path)
            file_names.append(file.filename)

        # Create batch task
        task_id = batch_processor.create_batch_task(
            file_paths=temp_file_paths,
            file_names=file_names,
            generate_answers=generate_answers,
            export_format=export_format
        )

        # Define processing function for single file
        def process_single_file(file_path: str, file_name: str, gen_ans: bool, exp_fmt: str) -> Dict:
            """Process a single file and return result"""
            try:
                # Process the file
                result = agent.process(
                    input_data=file_path,
                    export_format=exp_fmt,
                )

                if result.success and result.experience:
                    # Calculate processing time (will be updated by batch processor)
                    processing_time = 0.0

                    # Auto-save to database
                    experience_id = db.save_experience(result.experience, processing_time)

                    return {
                        "success": True,
                        "experience_id": experience_id,
                        "experience": result.experience.model_dump(),
                        "output_files": result.output_files,
                    }
                else:
                    return {
                        "success": False,
                        "error": result.error or "Processing failed"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

        # Start batch processing in background
        batch_processor.start_batch_processing(task_id, process_single_file)

        # Return task info
        return {
            "task_id": task_id,
            "total_files": len(files),
            "status": "processing",
            "message": f"Batch processing started for {len(files)} files"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/{task_id}")
async def get_batch_status(task_id: str):
    """
    Get the status of a batch processing task.

    Args:
        task_id: Task ID returned from batch upload endpoint

    Returns:
        Detailed batch task status including all sub-tasks
    """
    task_status = batch_processor.get_task_status(task_id)

    if task_status is None:
        raise HTTPException(status_code=404, detail="Batch task not found")

    return task_status


@app.get("/api/batch")
async def list_batch_tasks(status: Optional[str] = None):
    """
    List all batch processing tasks.

    Args:
        status: Optional status filter (pending, processing, completed, failed, cancelled)

    Returns:
        List of batch tasks
    """
    try:
        status_filter = None
        if status:
            try:
                status_filter = TaskStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status. Must be one of: {', '.join([s.value for s in TaskStatus])}"
                )

        tasks = batch_processor.get_all_tasks(status_filter)
        return {"tasks": tasks, "total": len(tasks)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/batch/{task_id}")
async def cancel_batch_task(task_id: str):
    """
    Cancel a pending batch task.

    Args:
        task_id: Task ID to cancel

    Returns:
        Cancellation status
    """
    success = batch_processor.cancel_task(task_id)

    if not success:
        task_status = batch_processor.get_task_status(task_id)
        if task_status is None:
            raise HTTPException(status_code=404, detail="Task not found")
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel task with status: {task_status['status']}"
            )

    return {"success": True, "message": "Task cancelled successfully"}


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
    notes: Optional[str] = None
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
        if request.notes is not None:
            experience.notes = request.notes
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
            q for q in experience.questions if not q.answer
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
                experience.questions[i].is_ai_generated = True
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


@app.get("/api/tasks/answer-generation/{task_id}")
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


@app.get("/api/tasks/answer-generation")
async def list_answer_generation_tasks(
    status: Optional[str] = Query(None, description="Filter by status: pending, processing, completed, failed")
):
    """
    List all active and recently completed answer generation tasks.

    Args:
        status: Optional filter by task status

    Returns:
        Dictionary containing list of tasks with their current status
    """
    tasks_list = []

    for task_id, task_data in answer_generation_tasks.items():
        # Filter by status if provided
        if status and task_data["status"] != status:
            continue

        tasks_list.append({
            "task_id": task_id,
            "experience_id": task_data["experience_id"],
            "status": task_data["status"],
            "progress": task_data["progress"],
            "total_questions": task_data["total_questions"],
            "created_at": task_data["created_at"],
            "completed_at": task_data.get("completed_at"),
        })

    return {"tasks": tasks_list}


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


class ExportRequest(BaseModel):
    """Request model for exporting experiences."""

    export_type: str = Field(..., description="Export type: by_interview | by_question")
    experience_ids: Optional[List[str]] = Field(default=None, description="Specific experience IDs to export")
    company_name: Optional[str] = Field(default=None, description="Filter by company name")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")


@app.post("/api/export")
async def export_markdown(request: ExportRequest):
    """
    Export interview experiences as markdown.

    Args:
        request: Export configuration

    Returns:
        Markdown content with download filename
    """
    try:
        if request.export_type == "by_interview":
            markdown_content = export_service.export_by_interview(
                experience_ids=request.experience_ids,
                company_name=request.company_name,
                tags=request.tags,
            )
            filename = f"interviews_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        elif request.export_type == "by_question":
            markdown_content = export_service.export_by_question(
                company_name=request.company_name,
                tags=request.tags,
            )
            filename = f"questions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid export_type. Must be 'by_interview' or 'by_question'"
            )

        return {
            "content": markdown_content,
            "filename": filename,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/excel")
async def export_excel(request: ExportRequest):
    """
    Export interview questions as Excel file.

    Args:
        request: Export configuration

    Returns:
        Excel file response
    """
    try:
        # Only support by_question export for Excel
        if request.export_type != "by_question":
            raise HTTPException(
                status_code=400,
                detail="Excel export only supports 'by_question' type"
            )

        excel_content = export_service.export_questions_to_excel(
            company_name=request.company_name,
            tags=request.tags,
        )

        filename = f"questions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        from fastapi.responses import Response

        return Response(
            content=excel_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Feishu Export API ============


@app.get("/api/feishu/status")
async def check_feishu_status():
    """
    Check if Feishu export is configured and test connection.

    Returns:
        Feishu configuration and connection status
    """
    try:
        status = export_service.test_feishu_connection()
        return status

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FeishuExportRequest(BaseModel):
    """Request model for Feishu export."""

    experience_ids: Optional[List[str]] = Field(default=None, description="Specific experience IDs to export")
    company_name: Optional[str] = Field(default=None, description="Filter by company name")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    folder_token: Optional[str] = Field(default=None, description="Feishu folder token to place documents in")
    create_index: bool = Field(default=True, description="Create an index document")


@app.post("/api/export/feishu")
async def export_to_feishu(request: FeishuExportRequest):
    """
    Export interview experiences to Feishu documents.

    Args:
        request: Export configuration

    Returns:
        Export results with document links
    """
    try:
        result = export_service.export_to_feishu(
            experience_ids=request.experience_ids,
            company_name=request.company_name,
            tags=request.tags,
            folder_token=request.folder_token,
            create_index=request.create_index
        )

        return result

    except Exception as e:
        if "not configured" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/experiences/{experience_id}/export/feishu")
async def export_single_experience_to_feishu(
    experience_id: str,
    folder_token: Optional[str] = None
):
    """
    Export a single interview experience to Feishu document.

    Args:
        experience_id: ID of the experience to export
        folder_token: Optional Feishu folder token

    Returns:
        Document information with link
    """
    try:
        result = export_service.export_single_to_feishu(
            experience_id=experience_id,
            folder_token=folder_token
        )

        return result

    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "not configured" in str(e).lower():
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============ 异步任务队列 API ============


@app.post("/api/process/text/async")
async def process_text_async(request: ProcessTextRequest):
    """
    异步处理文本内容（立即返回任务ID，后台处理）

    Args:
        request: 文本内容和处理选项

    Returns:
        任务ID和初始状态
    """
    try:
        # 验证内容
        is_valid, validation_score, validation_message = validate_content(request.content)

        if not is_valid:
            raise HTTPException(status_code=400, detail=validation_message)

        # 提交任务到队列
        task_id = task_queue.submit_task(
            task_type=TaskType.TEXT,
            input_data=request.content,
            generate_answers=request.generate_answers,
            export_format=request.export_format,
            metadata={
                "validation_score": validation_score,
                "validation_message": validation_message
            }
        )

        return {
            "task_id": task_id,
            "status": "queued",
            "message": "任务已提交到队列，将在后台处理"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process/images/async")
async def process_images_async(
    files: List[UploadFile] = File(...),
    generate_answers: bool = Form(False),
    export_format: str = Form("both"),
):
    """
    异步处理图片文件（立即返回任务ID，后台处理）

    Args:
        files: 上传的图片文件列表
        generate_answers: 是否生成答案
        export_format: 导出格式

    Returns:
        任务ID和初始状态
    """
    try:
        # 保存上传的文件到临时目录
        temp_dir = os.path.join(config.data_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)

        temp_file_paths = []
        file_names = []

        for idx, file in enumerate(files):
            temp_file_path = os.path.join(
                temp_dir, f"async_{int(time.time())}_{idx}_{file.filename}"
            )

            with open(temp_file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            temp_file_paths.append(temp_file_path)
            file_names.append(file.filename)

        # 提交任务到队列
        task_id = task_queue.submit_task(
            task_type=TaskType.IMAGE,
            input_data=temp_file_paths,
            generate_answers=generate_answers,
            export_format=export_format,
            metadata={
                "file_names": file_names,
                "file_count": len(files)
            }
        )

        return {
            "task_id": task_id,
            "status": "queued",
            "file_count": len(files),
            "message": f"任务已提交到队列，将处理 {len(files)} 个文件"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/async")
async def list_async_tasks(status: Optional[str] = None):
    """
    获取所有异步任务列表

    Args:
        status: 可选，按状态过滤 (queued, processing, completed, failed)

    Returns:
        任务列表
    """
    try:
        from src.utils.async_task_queue import TaskStatus as AsyncTaskStatus

        status_filter = None
        if status:
            # 验证状态值是否有效
            valid_statuses = {s.value for s in AsyncTaskStatus}
            if status not in valid_statuses:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                )
            # 传递字符串，让 get_all_tasks 内部进行比较
            status_filter = status

        tasks = task_queue.get_all_tasks(status_filter)

        # 转换为字典列表
        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "type": task.type.value if hasattr(task.type, 'value') else task.type,
                "status": task.status.value if hasattr(task.status, 'value') else task.status,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "processing_time": task.processing_time,
                "error": task.error,
                "metadata": task.metadata
            })

        return {"tasks": task_list, "total": len(task_list)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/async/{task_id}")
async def get_async_task_status(task_id: str):
    """
    查询异步任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务详细状态
    """
    task = task_queue.get_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "id": task.id,
        "type": task.type.value if hasattr(task.type, 'value') else task.type,
        "status": task.status.value if hasattr(task.status, 'value') else task.status,
        "created_at": task.created_at,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "processing_time": task.processing_time,
        "result": task.result,
        "error": task.error,
        "metadata": task.metadata
    }


@app.get("/api/tasks/queue/info")
async def get_queue_info():
    """
    获取队列统计信息

    Returns:
        队列状态统计
    """
    try:
        info = task_queue.get_queue_info()
        return info

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ API Configuration Endpoints ============


class ApiConfigResponse(BaseModel):
    """Response model for API configuration (masked)."""

    siliconflow_api_key: str = Field(..., description="Masked API key")
    siliconflow_api_base: str
    deepseek_model: str
    glm_vision_model: str


class UpdateApiConfigRequest(BaseModel):
    """Request model for updating API configuration."""

    siliconflow_api_key: Optional[str] = None
    siliconflow_api_base: Optional[str] = None
    deepseek_model: Optional[str] = None
    glm_vision_model: Optional[str] = None


@app.get("/api/config", response_model=ApiConfigResponse)
async def get_api_config():
    """
    Get current API configuration (with masked API key).

    Returns:
        Current configuration with masked API key
    """
    try:
        # Mask API key (show only last 4 characters)
        api_key = config.siliconflow_api_key
        masked_key = ""
        if api_key:
            if len(api_key) > 8:
                masked_key = "*" * (len(api_key) - 4) + api_key[-4:]
            else:
                masked_key = "*" * len(api_key)

        return ApiConfigResponse(
            siliconflow_api_key=masked_key,
            siliconflow_api_base=config.siliconflow_api_base,
            deepseek_model=config.deepseek_model,
            glm_vision_model=config.glm_vision_model,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config")
async def update_api_config(request: UpdateApiConfigRequest):
    """
    Update API configuration.

    Args:
        request: Configuration updates

    Returns:
        Success message and updated configuration
    """
    global config, agent

    try:
        # Update environment variables
        updated = False

        if request.siliconflow_api_key is not None:
            os.environ["SILICONFLOW_API_KEY"] = request.siliconflow_api_key
            config.siliconflow_api_key = request.siliconflow_api_key
            updated = True

        if request.siliconflow_api_base is not None:
            os.environ["SILICONFLOW_API_BASE"] = request.siliconflow_api_base
            config.siliconflow_api_base = request.siliconflow_api_base
            updated = True

        if request.deepseek_model is not None:
            os.environ["DEEPSEEK_MODEL"] = request.deepseek_model
            config.deepseek_model = request.deepseek_model
            updated = True

        if request.glm_vision_model is not None:
            os.environ["GLM_VISION_MODEL"] = request.glm_vision_model
            config.glm_vision_model = request.glm_vision_model
            updated = True

        if updated:
            # Reinitialize the agent with new config
            agent = InterviewAgent(config)

            # Update .env file
            env_path = ".env"
            if os.path.exists(env_path):
                # Read existing .env
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # Update values
                new_lines = []
                keys_updated = set()

                for line in lines:
                    if "=" in line and not line.strip().startswith("#"):
                        key = line.split("=")[0].strip()
                        if key == "SILICONFLOW_API_KEY" and request.siliconflow_api_key is not None:
                            new_lines.append(f"SILICONFLOW_API_KEY={request.siliconflow_api_key}\n")
                            keys_updated.add("SILICONFLOW_API_KEY")
                        elif key == "SILICONFLOW_API_BASE" and request.siliconflow_api_base is not None:
                            new_lines.append(f"SILICONFLOW_API_BASE={request.siliconflow_api_base}\n")
                            keys_updated.add("SILICONFLOW_API_BASE")
                        elif key == "DEEPSEEK_MODEL" and request.deepseek_model is not None:
                            new_lines.append(f"DEEPSEEK_MODEL={request.deepseek_model}\n")
                            keys_updated.add("DEEPSEEK_MODEL")
                        elif key == "GLM_VISION_MODEL" and request.glm_vision_model is not None:
                            new_lines.append(f"GLM_VISION_MODEL={request.glm_vision_model}\n")
                            keys_updated.add("GLM_VISION_MODEL")
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)

                # Add missing keys
                if request.siliconflow_api_key is not None and "SILICONFLOW_API_KEY" not in keys_updated:
                    new_lines.append(f"SILICONFLOW_API_KEY={request.siliconflow_api_key}\n")
                if request.siliconflow_api_base is not None and "SILICONFLOW_API_BASE" not in keys_updated:
                    new_lines.append(f"SILICONFLOW_API_BASE={request.siliconflow_api_base}\n")
                if request.deepseek_model is not None and "DEEPSEEK_MODEL" not in keys_updated:
                    new_lines.append(f"DEEPSEEK_MODEL={request.deepseek_model}\n")
                if request.glm_vision_model is not None and "GLM_VISION_MODEL" not in keys_updated:
                    new_lines.append(f"GLM_VISION_MODEL={request.glm_vision_model}\n")

                # Write back to .env
                with open(env_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)

        # Mask API key for response
        api_key = config.siliconflow_api_key
        masked_key = ""
        if api_key:
            if len(api_key) > 8:
                masked_key = "*" * (len(api_key) - 4) + api_key[-4:]
            else:
                masked_key = "*" * len(api_key)

        return {
            "success": True,
            "message": "Configuration updated successfully",
            "config": {
                "siliconflow_api_key": masked_key,
                "siliconflow_api_base": config.siliconflow_api_base,
                "deepseek_model": config.deepseek_model,
                "glm_vision_model": config.glm_vision_model,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
