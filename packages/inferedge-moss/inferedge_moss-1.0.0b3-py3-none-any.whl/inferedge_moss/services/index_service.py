# index_service.py
from __future__ import annotations

from typing import Dict, List, Literal, Optional

from moss_core import Index  # PyO3-bound Rust class
from moss_core import (
    AddDocumentsOptions,
    DocumentInfo,
    GetDocumentsOptions,
    IndexInfo,
    SearchResult,
    SerializedIndex,
)

from .embedding_service import EmbeddingService

MossModel = Literal["moss-minilm", "moss-mediumlm"]


class IndexService:
    def __init__(self) -> None:
        # In-memory registry of indices, backed by Rust via PyO3
        self._indexes: Dict[str, Index] = {}
        # Track the model id for each index so we can embed with the right model
        self._index_models: Dict[str, str] = {}
        # Store full document information for query result mapping
        self._index_documents: Dict[str, Dict[str, DocumentInfo]] = {}

    # ---------- Index lifecycle ----------

    async def create_index(
        self,
        index_name: str,
        docs: List[DocumentInfo],
        model_id: str | MossModel,
    ) -> None:
        if index_name in self._indexes:
            raise ValueError(f"Index with name '{index_name}' already exists")

        model_str = str(model_id)
        # Create Rust index (sync)
        index = Index(index_name, model_str)

        # Compute embeddings in Python (async), then add to Rust index (sync)
        embedding_service = EmbeddingService(
            model_id=model_str, normalize=True, quantized=False
        )
        await embedding_service.load_model()
        embeddings = [await embedding_service.create_embedding(d.text) for d in docs]

        # Rust method is sync and returns (added, updated)
        index.add_documents(docs, embeddings)

        # Register
        self._indexes[index_name] = index
        self._index_models[index_name] = model_str
        # Store documents for query mapping
        self._index_documents[index_name] = {doc.id: doc for doc in docs}

    async def create_index_from_serialized(
        self, data: SerializedIndex, documents: Optional[List[DocumentInfo]] = None
    ) -> Index:
        if data.name in self._indexes:
            raise ValueError(f"Index with name '{data.name}' already exists")

        # Construct with the serialized model id
        index = Index(data.name, data.model.id)
        # Rust deserialize is sync
        index.deserialize(data)

        self._indexes[data.name] = index
        self._index_models[data.name] = data.model.id

        # Store documents for query mapping if provided
        if documents:
            self._index_documents[data.name] = {doc.id: doc for doc in documents}
        else:
            self._index_documents[data.name] = {}

        return index

    def get_index_info(self, index_name: str) -> IndexInfo:
        index = self._indexes.get(index_name)
        if not index:
            raise KeyError(f"Index '{index_name}' not found")
        return index.get_info()

    def list_indexes(self) -> List[IndexInfo]:
        return [idx.get_info() for idx in self._indexes.values()]

    def delete_index(self, index_name: str) -> None:
        if index_name not in self._indexes:
            raise KeyError(f"Index '{index_name}' not found")
        del self._indexes[index_name]
        self._index_models.pop(index_name, None)
        self._index_documents.pop(index_name, None)

    # ---------- Document operations ----------

    async def add_documents(
        self,
        index_name: str,
        docs: List[DocumentInfo],
        options: Optional[AddDocumentsOptions] = None,
    ) -> dict:
        index = self._indexes.get(index_name)
        if not index:
            raise KeyError(f"Index '{index_name}' not found")

        model_str = self._index_models[index_name]
        embedding_service = EmbeddingService(
            model_id=model_str, normalize=True, quantized=False
        )
        await embedding_service.load_model()
        embeddings = [await embedding_service.create_embedding(d.text) for d in docs]

        # Sync call; returns (added, updated)
        if options is None:
            added, updated = index.add_documents(docs, embeddings)
        else:
            added, updated = index.add_documents(docs, embeddings, options)

        return {"added": int(added), "updated": int(updated)}

    async def delete_documents(self, index_name: str, doc_ids: List[str]) -> dict:
        index = self._indexes.get(index_name)
        if not index:
            raise KeyError(f"Index '{index_name}' not found")

        # Sync call; returns count
        deleted = index.delete_documents(doc_ids)
        return {"deleted": int(deleted)}

    def get_documents(
        self,
        index_name: str,
        options: Optional[GetDocumentsOptions] = None,
    ) -> List[DocumentInfo]:
        index = self._indexes.get(index_name)
        if not index:
            raise KeyError(f"Index '{index_name}' not found")
        return index.get_documents(options)

    # ---------- Querying ----------

    async def query(self, index_name: str, query: str, top_k: int = 5) -> SearchResult:
        import time

        start_time = time.time()

        index = self._indexes.get(index_name)
        if not index:
            raise KeyError(f"Index '{index_name}' not found")

        model_str = self._index_models[index_name]
        embedding_service = EmbeddingService(
            model_id=model_str, normalize=True, quantized=False
        )
        await embedding_service.load_model()
        q_emb = await embedding_service.create_embedding(query)

        # Get raw query results from Rust (IDs and scores only)
        raw_result = index.query(query, top_k, q_emb)

        # Get stored documents for this index
        doc_map = self._index_documents.get(index_name, {})

        # Map results back to full document information
        populated_docs = []
        for result_doc in raw_result.docs:
            if result_doc.id in doc_map:
                full_doc = doc_map[result_doc.id]
                # Create a new result doc with full information
                populated_doc = type(
                    "QueryResultDoc",
                    (),
                    {
                        "id": result_doc.id,
                        "score": result_doc.score,
                        "text": full_doc.text,
                        "metadata": getattr(full_doc, "metadata", None),
                    },
                )()
                populated_docs.append(populated_doc)

        # Calculate timing
        time_taken_ms = int((time.time() - start_time) * 1000)

        # Return SearchResult with populated documents
        return type(
            "SearchResult",
            (),
            {
                "docs": populated_docs,
                "query": query,
                "index_name": index_name,
                "time_taken_ms": time_taken_ms,
            },
        )()

    # ---------- Serialization ----------

    def serialize_index(self, index_name: str) -> SerializedIndex:
        index = self._indexes.get(index_name)
        if not index:
            raise KeyError(f"Index '{index_name}' not found")
        return index.serialize()

    # ---------- Utilities ----------

    def has_index(self, index_name: str) -> bool:
        return index_name in self._indexes

    def get_index(self, index_name: str) -> Optional[Index]:
        return self._indexes.get(index_name)
