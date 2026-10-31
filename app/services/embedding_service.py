from langchain_voyageai import VoyageAIEmbeddings

from app.config.settings import get_settings


def get_embeddings() -> VoyageAIEmbeddings:
    settings = get_settings()
    return VoyageAIEmbeddings(
        api_key=settings.voyage_api_key,
        model=settings.embedding_model,
    );