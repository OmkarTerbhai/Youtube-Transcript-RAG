from app.config.settings import get_settings;
from app.services.DocumentService import DocumentService;
from app.repositories.vector_store_repo import VectorStoreRepository;
from pathlib import Path;
from uuid import uuid4;

class IngestionService :

    def __init__(self):
        self.settings = get_settings();
        self.document_svc = DocumentService(200, 20);
        self.vector_store_repo = VectorStoreRepository();

    def _save_upload_batch(self, file_pairs: list[tuple[str, bytes]]) -> tuple[str, list[Path]]:
        """Save received docs in server disk storage"""

        batch_id = str(uuid4());
        batch_dir: Path = Path(self.settings.upload_dir) / batch_id;
        batch_dir.mkdir(parents=True, exist_ok=True);

        paths: list[Path] = [];

        for file_name, file_content in file_pairs :
            safe_name = Path(file_name).name;
            dest = batch_dir / safe_name;
            dest.write_bytes(file_content);
            paths.append(dest);

        return batch_id, paths;

    def _ingest_file_at_path(self, file_path: Path, source_name: str) -> dict :
        """Ingest a single file and add it to the vector store"""

        name = source_name or file_path.name;
        chunks = self.document_svc.process_file(file_path=file_path, source_name=name);
        if not chunks :
            return {"filename": name, "chunks_created": 0,
                    "document_ids": []};
        ids = self.vector_store_repo.add_docs(chunks);

        return {"filename": name, "chunks_created": len(chunks),
                "document_ids": ids};

    def ingest_files_sync(self, file_pairs: list[tuple[str, bytes]]) -> dict :
        """Upload files in server storage and ingest them to
        the vector store"""

        if not file_pairs:
            raise ValueError("No files provided");

        res = [];

        _, paths = self._save_upload_batch(file_pairs=file_pairs);

        for path in paths :
            res.append(self._ingest_file_at_path(path, path.name));

        total_chunks: int = sum(result["chunks_created"]
                                for result in res);

        return {
            "files": res,
            "chunks_created": total_chunks,
            "total_files": len(res),
            "msg": "Documents uploaded, split, indexed successfully"
        };