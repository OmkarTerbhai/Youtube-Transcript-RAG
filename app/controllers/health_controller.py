from fastapi import APIRouter;
from datetime import datetime;
from app.models.HealthResponse import HealthResponse

router = APIRouter(
    prefix = "/health",
    tags = ["health"]
);

@router.get("",response_model=HealthResponse)
async def health_check() -> HealthResponse :
    """Basic Health check endpoint"""
    return HealthResponse(
        status="ok/healthy",
        timestamp=datetime.now()
    );


