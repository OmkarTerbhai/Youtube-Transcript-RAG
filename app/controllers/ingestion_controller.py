from fastapi import APIRouter, UploadFile as FastAPIUploadFile, File, HTTPException
from app.config.settings import get_settings
from app.services.IngestionService import IngestionService
from app.models.HealthResponse import DocumentBatchUploadResponse
from typing import Annotated, List
# 1. Import WithJsonSchema from pydantic
from pydantic import WithJsonSchema

# 2. Define a custom UploadFile type that forces Swagger to render the file picker
UploadFile = Annotated[FastAPIUploadFile, WithJsonSchema({"type": "string", "format": "binary"})]

router = APIRouter(prefix="/docs", tags=["document"])

@router.post(
    "/upload",
    summary="Upload a document to be added to vector store",
    response_model=None
)
async def upload_docs(
    # 3. Your function argument remains clean, using our overridden type alias
    files: Annotated[List[UploadFile], File()]
):
    settings = get_settings()

    if not files:
        raise HTTPException(status_code=400)
    if len(files) > settings.max_files_per_upload:
        raise HTTPException(status_code=400)

    file_pairs: list[tuple[str, bytes]] = []

    for file in files:
        content = await file.read()
        file_pairs.append((file.filename, content))

    svc = IngestionService()

    try:
        payload = svc.ingest_files_sync(file_pairs=file_pairs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return DocumentBatchUploadResponse(
        chunks_created=payload["chunks_created"],
        files=payload["files"],
        files_total=payload["total_files"],
        message=payload["msg"]
    )
