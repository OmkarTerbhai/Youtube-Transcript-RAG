from app.config.settings import get_settings;
from app.repositories.vector_store_repo import VectorStoreRepository;
from langchain_core.documents import Document;
from dotenv import load_dotenv;
from langchain_openrouter import ChatOpenRouter

class QueryService :

    def __init__(self):
        self.settings = get_settings();
        self.vector_store_repo = VectorStoreRepository();

    def _find_similar_docs(self, query: str) -> list[str] :
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

    def answer_query(self, query: str):
        """Send retrieved context to LLM to get the answer to the query"""

        relevant_facts = self._find_similar_docs(query=query);
        context = "\n".join(f" = {d["content"]}"
                            for d in relevant_facts);
        prompt = (
            "Answer the following question only on the notes provided\n"
            "If the notes don't contain the answer, say 'No Info found, Sorry!'\n"
            f"Notes: \n{context}\n\n Question: \n\t{query}"
        );

        llm = ChatOpenRouter(
            model="nvidia/nemotron-3-ultra-550b-a55b",  # Swap with any OpenRouter model slug
            temperature=0.7,
            api_key=self.settings.openrouter_api_key
        )

        # 2. Invoke the model
        response = llm.invoke(prompt);

        return response.content;

