from app.config.settings import get_settings;
from app.repositories.vector_store_repo import VectorStoreRepository;
from langchain_core.documents import Document;

class QueryService :

    def __init__(self):
        self.settings = get_settings();
        self.vector_store_repo = VectorStoreRepository();

    def find_similar_docs(self, query: str) -> list[str] :
        """Send query to vector store and get `k` similar docs"""

        if not query:
            raise ValueError("Query is not provided...");

        res: list[Document] = [];
        sim_k: int = self.settings.retrieval_k;

        res = self.vector_store_repo.search_with_score(query=query, k=sim_k);
        print(res);
        return [
            {"content": r.page_content}
            for r in res
        ];

