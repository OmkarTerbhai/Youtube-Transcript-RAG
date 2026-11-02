from fastapi import APIRouter;
from app.services.CSVService import CSVService;

router = APIRouter(prefix="/generate", tags=["generate"])

@router.post(
    "/",
    summary="Generate a csv",
    response_model=None
)
async def accept_query(
      url: str
) :
    query_svc = CSVService();
    res_json = query_svc.build_rows(url=url);

    return res_json;