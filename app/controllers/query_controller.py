from fastapi import APIRouter, UploadFile as FastAPIUploadFile, File, HTTPException
from app.services.QueryService import QueryService;

router = APIRouter(prefix="/query", tags=["query"])

@router.post(
    "/ask",
    summary="Ask query to vector store",
    response_model=None
)
async def accept_query(
      query: str
) :
    query_svc = QueryService();
    res_json = query_svc.find_similar_docs(query=query);

    return res_json;