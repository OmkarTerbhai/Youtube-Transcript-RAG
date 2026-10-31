from ..config.settings import Settings;
from langchain_text_splitters import RecursiveCharacterTextSplitter;
from pathlib import Path;
import csv;
from langchain_core.documents import Document;

class DocumentService :
    """Service for document processing"""

    SUPPORTED_FILE_EXT = {".csv"};

    TRANSCRIPT_CSV_FIELDNAMES = {
        "id",
        "start",
        "end",
        "url",
        "channel_id",
        "title",
        "published",
        "text"
    };

    def __init__(self, chunk_size: int, chunk_overlap: int):
        settings = Settings();
        self.chunk_size = chunk_size;
        self.chunk_overlap = chunk_overlap;
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " " ""],
            length_function=len
        );

    def _is_transcript_csv(self, file_path: Path)-> bool:

        with file_path.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            if not reader.fieldnames :
                return False;
            else :
                fields = set[str](reader.fieldnames);
                print(fields);
                return self.TRANSCRIPT_CSV_FIELDNAMES.issubset(fields);

    def _load_transcript_csv(self, file_path: Path, source_name: str) -> list[Document]:
        """Load a transcript CSV file into langchain documents
        containing text and other attributes in metadata"""

        documents: list[Document] = [];

        with file_path.open(newline="", encoding="utf-8") as file :
            reader = csv.DictReader(file);

            for row in reader :
                text = row.get("text", "").strip();

                if not text :
                    continue;

                metadata = {
                    "source": source_name,
                    "id": row.get("id", ""),
                    "start": row.get("start", ""),
                    "end": row.get("end", ""),
                    "url": row.get("url", ""),
                    "channel_id": row.get("title", ""),
                    "title": row.get("title", ""),
                    "publisher": row.get("publisher", "")
                };

                documents.append(Document(page_content=text, metadata=metadata));
            return documents;

    def _load_file(self, file_path: Path, source: str | None) -> list[Document]:

        file_path = Path(file_path);
        file_name: str = source or file_path.name;

        file_extension: str = file_path.suffix.lower();

        if file_extension not in self.SUPPORTED_FILE_EXT:
            raise ValueError(f"Invalid extension {file_extension}");

        if ".csv" == file_extension :
            if self._is_transcript_csv(file_path) :
                docs: list[Document] = self._load_transcript_csv(file_path, file_name);
            else :
                raise ValueError("Not a supported csv");
        else :
            raise ValueError(f"Unsupported file extension: {ext}");

        return docs;

    def _split_documents(self, documents: list[Document]) -> list[Document]:

        return self.text_splitter.split_documents(documents);

    def process_file(self, file_path: Path, source_name: str | None) -> list[Document]:
        docs = self._load_file(file_path=file_path, source=source_name);
        return self._split_documents(documents=docs);





