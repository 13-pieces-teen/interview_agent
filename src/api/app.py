"""FastAPI application for interview agent."""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import time
from datetime import datetime

from src.main import InterviewAgent
from src.utils.config import Config
from src.models.schema import InterviewExperience

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
    output_files: List[str] = []
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str
    version: str


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

        # Process the interview experience
        result = agent.process(
            input_data=request.content,
            generate_answers=request.generate_answers,
            export_format=request.export_format,
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
                generate_answers=generate_answers,
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
                generate_answers=generate_answers,
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
