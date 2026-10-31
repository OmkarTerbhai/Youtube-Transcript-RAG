import uuid_utils
from qdrant_client import QdrantClient;
from qdrant_client.http.models import Distance;
from app.config.settings import get_settings;
from langchain_qdrant import QdrantVectorStore;
from app.services.embedding_service import get_embeddings;
from doctest import UnexpectedException;
from qdrant_client.models import VectorParams;
from langchain_core.documents import Document;

def get_qdrant_client() -> QdrantClient :
    settings = get_settings();
    return QdrantClient(
        url=settings.qdrant_url
    );

class VectorStoreRepository :

    def __init__(self, collection_name: str | None = None):
        settings = get_settings();
        self.collection_name = collection_name or settings.collection_name
        self.client = get_qdrant_client();
        self._vector_store: QdrantVectorStore | None = None;

    @property
    def vector_store(self)-> QdrantVectorStore :
        if self._vector_store is None :
            self._vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=get_embeddings()
            );

        return self._vector_store;

    def _ensure_collection(self):
        try :
            _info = self.client.get_collection(self.collection_name);

        except UnexpectedException :
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=get_embeddings().output_dimension,
                    distance=Distance.COSINE
                )
            );

    def add_docs(self, documents: list[Document])->list[str] :
        if not documents :
            return []

        ids = [str(uuid_utils.uuid4()) for _ in documents];
        self._ensure_collection();
        self.vector_store.add_documents(documents=documents, ids=ids);
        return ids;

    def delete_collection(self):
        self.client.delete_collection(self.collection_name);

    def search_with_score(self, query: str, k :int)->list[tuple[Document, float]]:
        settings = get_settings();
        k = k or settings.retrieval_k;
        return self.vector_store.similarity_search(query=query, k=k);

    def health_check(self) -> bool :
        try :
            self.client.get_collection(self.collection_name);
            return True;
        except Exception as e :
            return False;