# vectordb/store.py

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


# ==========================
# Base Abstract Vector Store
# ==========================
class BaseVectorStore(ABC):
    """Abstract class for all vector database operations."""

    @abstractmethod
    def insert_vectors(self, vectors, metadata=None):
        """Insert embeddings and metadata into vector DB."""
        pass

    @abstractmethod
    def search_vectors(self, query_vector, top_k=5):
        """Search for similar vectors."""
        pass

    @abstractmethod
    def update_vector(self, vector_id, new_vector, metadata=None):
        """Update existing vector."""
        pass

    @abstractmethod
    def delete_vector(self, vector_id):
        """Delete a vector from DB."""
        pass


# =======================
# Local ChromaDB Handling (new PersistentClient API)
# =======================
class ChromaVectorStore(BaseVectorStore):
    def __init__(self, persist_directory: str = "data/chroma_store"):
        try:
            from chromadb import PersistentClient
        except Exception as e:
            raise RuntimeError("chromadb is required for ChromaVectorStore: pip install chromadb") from e

        # Use PersistentClient with path to persist_directory
        self.client = PersistentClient(path=persist_directory)
        # collection name
        self.collection = self.client.get_or_create_collection(name="text_embeddings")
        logger.info(f"Initialized local ChromaDB at {persist_directory}")

    def insert_vectors(self, vectors, metadata=None):
        # Expect vectors: list of lists (embeddings)
        ids = [f"id_{i}" for i in range(len(vectors))]
        metadatas = metadata if metadata is not None else [{} for _ in range(len(vectors))]
        # chroma expects embeddings as list of vectors
        self.collection.add(ids=ids, embeddings=vectors, metadatas=metadatas, documents=[m.get("text", "") for m in metadatas])
        logger.info(f"Inserted {len(vectors)} vectors into ChromaDB")

    def search_vectors(self, query_vector, top_k=5):
        # chroma returns a dict-like structure; we return it as-is
        results = self.collection.query(query_embeddings=[query_vector], n_results=top_k)
        return results

    def update_vector(self, vector_id, new_vector, metadata=None):
        # Chroma supports update by id
        self.collection.update(ids=[vector_id], embeddings=[new_vector], metadatas=[metadata or {}])
        logger.info(f"Updated vector ID: {vector_id}")

    def delete_vector(self, vector_id):
        self.collection.delete(ids=[vector_id])
        logger.info(f"Deleted vector ID: {vector_id}")


# ======================
# Cloud Pinecone Handler
# ======================
class PineconeVectorStore(BaseVectorStore):
    def __init__(self, api_key: str, index_name: str, dimension: int = 1536):
        try:
            import pinecone
        except Exception as e:
            raise RuntimeError("pinecone-client is required for PineconeVectorStore: pip install pinecone-client") from e

        pinecone.init(api_key=api_key)
        self.index_name = index_name

        if index_name not in pinecone.list_indexes():
            pinecone.create_index(index_name, dimension=dimension, metric="cosine")

        self.index = pinecone.Index(index_name)
        logger.info(f"Connected to Pinecone index: {index_name}")

    def insert_vectors(self, vectors, metadata=None):
        items = [(f"id_{i}", vectors[i], metadata[i] if metadata else {}) for i in range(len(vectors))]
        self.index.upsert(vectors=items)
        logger.info(f"Inserted {len(vectors)} vectors into Pinecone")

    def search_vectors(self, query_vector, top_k=5):
        return self.index.query(vector=query_vector, top_k=top_k, include_metadata=True)

    def update_vector(self, vector_id, new_vector, metadata=None):
        self.index.upsert(vectors=[(vector_id, new_vector, metadata or {})])
        logger.info(f"Updated vector ID: {vector_id}")

    def delete_vector(self, vector_id):
        self.index.delete(ids=[vector_id])
        logger.info(f"Deleted vector ID: {vector_id}")


# =====================
# Store Factory Utility
# =====================
def get_vector_store(store_type: str = "chroma", config: dict = None):
    """
    Factory method to select vector store.
    :param store_type: "chroma" or "pinecone"
    :param config: dict with credentials or paths
    """
    config = config or {}
    store_type = store_type.lower()
    if store_type == "pinecone":
        return PineconeVectorStore(
            api_key=config.get("api_key"),
            index_name=config.get("index_name"),
            dimension=config.get("dimension", 1536)
        )
    elif store_type == "chroma":
        return ChromaVectorStore(
            persist_directory=config.get("persist_directory", "data/chroma_store")
        )
    else:
        raise ValueError(f"Unsupported vector store type: {store_type}")
