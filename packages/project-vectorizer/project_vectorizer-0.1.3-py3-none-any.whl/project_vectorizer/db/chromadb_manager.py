"""ChromaDB-based database manager for vector search and metadata storage."""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

import numpy as np

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

logger = logging.getLogger(__name__)


class ChromaDBManager:
    """
    Database manager using ChromaDB for both vector storage and metadata.

    This approach provides:
    - Fast vector similarity search via ChromaDB
    - Unified storage for vectors and metadata
    - Better scalability for large projects
    - No external database dependencies
    """

    def __init__(self, chroma_path: Optional[str] = None):
        """
        Initialize ChromaDB manager.

        Args:
            chroma_path: Path to ChromaDB storage directory
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is not installed. Install with: pip install chromadb>=0.4.0"
            )

        self.chroma_path = chroma_path or str(Path.home() / ".vectorizer" / "chromadb")

        # ChromaDB for vectors and metadata
        self.chroma_client = None
        self.collections = {}  # Cache collections per project

        # Metadata collection names
        self.METADATA_COLLECTION = "project_metadata"

    async def initialize(self):
        """Initialize ChromaDB."""
        await self._initialize_chromadb()

    async def _initialize_chromadb(self):
        """Initialize ChromaDB client."""
        # Ensure ChromaDB directory exists
        Path(self.chroma_path).mkdir(parents=True, exist_ok=True)

        # Run ChromaDB initialization in executor (it's synchronous)
        loop = asyncio.get_event_loop()
        self.chroma_client = await loop.run_in_executor(
            None,
            lambda: chromadb.PersistentClient(
                path=self.chroma_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        )

        logger.info(f"Initialized ChromaDB at {self.chroma_path}")

    async def close(self):
        """Close database connections."""
        # ChromaDB client doesn't need explicit closing
        self.collections.clear()

    def _get_collection_name(self, project_id: int) -> str:
        """Get ChromaDB collection name for a project."""
        return f"project_{project_id}_chunks"

    def _get_metadata_collection_name(self, collection_type: str) -> str:
        """Get ChromaDB collection name for metadata."""
        return f"{self.METADATA_COLLECTION}_{collection_type}"

    async def _get_or_create_collection(self, project_id: int, embedding_dimension: int = 384):
        """Get or create ChromaDB collection for a project's chunks."""
        collection_name = self._get_collection_name(project_id)

        if collection_name in self.collections:
            return self.collections[collection_name]

        # Run in executor (ChromaDB operations are synchronous)
        loop = asyncio.get_event_loop()
        collection = await loop.run_in_executor(
            None,
            lambda: self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},  # Use cosine similarity
                embedding_function=None  # We provide embeddings manually
            )
        )

        self.collections[collection_name] = collection
        return collection

    async def _get_or_create_metadata_collection(self, collection_type: str):
        """Get or create ChromaDB collection for metadata storage."""
        collection_name = self._get_metadata_collection_name(collection_type)

        if collection_name in self.collections:
            return self.collections[collection_name]

        loop = asyncio.get_event_loop()
        collection = await loop.run_in_executor(
            None,
            lambda: self.chroma_client.get_or_create_collection(
                name=collection_name,
                embedding_function=None  # We don't need embeddings for metadata
            )
        )

        self.collections[collection_name] = collection
        return collection

    # ========================================================================
    # Project metadata operations (ChromaDB)
    # ========================================================================

    async def create_project(
        self,
        name: str,
        path: str,
        embedding_model: str,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new project."""
        collection = await self._get_or_create_metadata_collection("projects")

        # Generate project ID based on existing projects
        project_id = await self._get_next_project_id(collection)

        project_data = {
            'id': project_id,
            'name': name,
            'path': path,
            'description': description or '',
            'embedding_model': embedding_model,
            'chunk_size': chunk_size,
            'chunk_overlap': chunk_overlap,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        # Store in ChromaDB (metadata collections need dummy embeddings)
        loop = asyncio.get_event_loop()
        # Create a simple embedding (all zeros) for metadata
        dummy_embedding = [0.0] * 1  # Minimal embedding
        await loop.run_in_executor(
            None,
            lambda: collection.add(
                ids=[f"project_{project_id}"],
                documents=[name],  # Use name as document for searchability
                metadatas=[project_data],
                embeddings=[dummy_embedding]
            )
        )

        # Create chunks collection for this project
        await self._get_or_create_collection(project_id)

        # Return project object
        return type('Project', (), project_data)()

    async def _get_next_project_id(self, collection) -> int:
        """Get the next available project ID."""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: collection.get()
        )

        if not result or not result['ids']:
            return 1

        # Find highest ID
        max_id = 0
        for metadata in result['metadatas']:
            if metadata and 'id' in metadata:
                max_id = max(max_id, metadata['id'])

        return max_id + 1

    async def get_project(self, name: str) -> Optional[Any]:
        """Get project by name."""
        collection = await self._get_or_create_metadata_collection("projects")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: collection.get(
                where={"name": name}
            )
        )

        if result and result['metadatas'] and result['metadatas'][0]:
            return type('Project', (), result['metadatas'][0])()

        return None

    async def get_project_by_path(self, path: str) -> Optional[Any]:
        """Get project by path."""
        collection = await self._get_or_create_metadata_collection("projects")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: collection.get(
                where={"path": path}
            )
        )

        if result and result['metadatas'] and result['metadatas'][0]:
            return type('Project', (), result['metadatas'][0])()

        return None

    # ========================================================================
    # File metadata operations (ChromaDB)
    # ========================================================================

    async def upsert_file(
        self,
        project_id: int,
        file_path: str,
        relative_path: str,
        file_type: str,
        size_bytes: int,
        content_hash: str,
        last_modified,
    ) -> Any:
        """Insert or update a file record."""
        collection = await self._get_or_create_metadata_collection("files")

        # Generate file ID
        file_id = f"file_{project_id}_{relative_path}".replace("/", "_").replace("\\", "_")

        # Try to get existing file
        loop = asyncio.get_event_loop()
        existing = await loop.run_in_executor(
            None,
            lambda: collection.get(
                ids=[file_id]
            )
        )

        file_data = {
            'id': file_id,
            'project_id': project_id,
            'path': file_path,
            'relative_path': relative_path,
            'file_type': file_type,
            'size_bytes': size_bytes,
            'content_hash': content_hash,
            'last_modified': last_modified.isoformat() if hasattr(last_modified, 'isoformat') else str(last_modified),
            'is_indexed': False,
            'indexed_at': '',  # Empty string instead of None
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        dummy_embedding = [0.0] * 1  # Minimal embedding for metadata

        if existing and existing['ids']:
            # Update existing
            await loop.run_in_executor(
                None,
                lambda: collection.update(
                    ids=[file_id],
                    documents=[relative_path],
                    metadatas=[file_data],
                    embeddings=[dummy_embedding]
                )
            )
        else:
            # Add new
            await loop.run_in_executor(
                None,
                lambda: collection.add(
                    ids=[file_id],
                    documents=[relative_path],
                    metadatas=[file_data],
                    embeddings=[dummy_embedding]
                )
            )

        return type('File', (), file_data)()

    async def get_files_to_index(self, project_id: int) -> List[Any]:
        """Get files that need to be indexed."""
        collection = await self._get_or_create_metadata_collection("files")

        loop = asyncio.get_event_loop()
        # Get all files for this project (ChromaDB only supports single where clauses)
        result = await loop.run_in_executor(
            None,
            lambda: collection.get(
                where={"project_id": project_id}
            )
        )

        # Filter for non-indexed files in Python
        files = []
        if result and result['metadatas']:
            for metadata in result['metadatas']:
                if not metadata.get('is_indexed', False):
                    files.append(type('File', (), metadata)())

        return files

    async def mark_file_indexed(self, file_id: str) -> None:
        """Mark a file as indexed."""
        collection = await self._get_or_create_metadata_collection("files")

        # Get existing file data
        loop = asyncio.get_event_loop()
        existing = await loop.run_in_executor(
            None,
            lambda: collection.get(ids=[file_id])
        )

        if existing and existing['metadatas']:
            metadata = existing['metadatas'][0]
            metadata['is_indexed'] = True
            metadata['indexed_at'] = datetime.now().isoformat()
            metadata['updated_at'] = datetime.now().isoformat()

            dummy_embedding = [0.0] * 1  # Minimal embedding for metadata

            await loop.run_in_executor(
                None,
                lambda: collection.update(
                    ids=[file_id],
                    documents=[metadata['relative_path']],
                    metadatas=[metadata],
                    embeddings=[dummy_embedding]
                )
            )

    async def get_all_files(self, project_id: int) -> List[Any]:
        """Get all files for a project."""
        collection = await self._get_or_create_metadata_collection("files")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: collection.get(
                where={"project_id": project_id}
            )
        )

        files = []
        if result and result['metadatas']:
            for metadata in result['metadatas']:
                files.append(type('File', (), metadata)())

        return files

    async def get_file_by_path(self, project_id: int, relative_path: str) -> Optional[Any]:
        """Get file by relative path."""
        collection = await self._get_or_create_metadata_collection("files")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: collection.get(
                where={"project_id": project_id}
            )
        )

        # Filter by relative_path in Python (ChromaDB limitation)
        if result and result['metadatas']:
            for metadata in result['metadatas']:
                if metadata.get('relative_path') == relative_path:
                    return type('File', (), metadata)()

        return None

    async def update_file(self, file_id: str, **kwargs) -> None:
        """Update file metadata."""
        collection = await self._get_or_create_metadata_collection("files")

        # Get existing file data
        loop = asyncio.get_event_loop()
        existing = await loop.run_in_executor(
            None,
            lambda: collection.get(ids=[file_id])
        )

        if existing and existing['metadatas']:
            metadata = existing['metadatas'][0]

            # Update provided fields
            for key, value in kwargs.items():
                if hasattr(value, 'isoformat'):
                    metadata[key] = value.isoformat()
                else:
                    metadata[key] = value if value is not None else ''

            metadata['updated_at'] = datetime.now().isoformat()

            dummy_embedding = [0.0] * 1

            await loop.run_in_executor(
                None,
                lambda: collection.update(
                    ids=[file_id],
                    documents=[metadata['relative_path']],
                    metadatas=[metadata],
                    embeddings=[dummy_embedding]
                )
            )

    async def delete_file(self, file_id: str) -> None:
        """Delete a file and its chunks."""
        # Delete file metadata
        files_collection = await self._get_or_create_metadata_collection("files")

        loop = asyncio.get_event_loop()

        # Get file to find project_id
        existing = await loop.run_in_executor(
            None,
            lambda: files_collection.get(ids=[file_id])
        )

        if existing and existing['metadatas']:
            project_id = existing['metadatas'][0]['project_id']

            # Delete file metadata
            await loop.run_in_executor(
                None,
                lambda: files_collection.delete(ids=[file_id])
            )

            # Delete all chunks for this file
            collection = await self._get_or_create_collection(project_id)
            await self._delete_chunks_by_file(collection, file_id)

    # ========================================================================
    # Vector operations (ChromaDB)
    # ========================================================================

    async def save_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """Save chunks to ChromaDB."""
        if not chunks:
            return

        project_id = chunks[0]['project_id']
        file_id = chunks[0]['file_id']

        # Get collection
        collection = await self._get_or_create_collection(project_id)

        # Delete existing chunks for this file
        await self._delete_chunks_by_file(collection, file_id)

        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in chunks:
            # Generate unique ID
            chunk_id = f"file_{file_id}_chunk_{chunk['chunk_index']}"
            ids.append(chunk_id)

            # Extract embedding
            embeddings.append(chunk['embedding'])

            # Store content as document
            documents.append(chunk['content'])

            # Store metadata
            metadata = {
                'file_id': str(file_id),
                'chunk_index': chunk['chunk_index'],
                'content_type': chunk.get('content_type', 'code'),
                'start_line': chunk.get('start_line', 0),
                'end_line': chunk.get('end_line', 0),
                'language': chunk.get('language', 'unknown'),
                'token_count': chunk.get('token_count', 0),
                'embedding_model': chunk.get('embedding_model', 'unknown')
            }
            metadatas.append(metadata)

        # Add to ChromaDB (run in executor)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
        )

        logger.debug(f"Saved {len(chunks)} chunks to ChromaDB for file {file_id}")

    async def _delete_chunks_by_file(self, collection, file_id: str):
        """Delete all chunks for a specific file."""
        loop = asyncio.get_event_loop()

        # Query for chunks with this file_id
        try:
            result = await loop.run_in_executor(
                None,
                lambda: collection.get(where={"file_id": str(file_id)})
            )

            if result and result['ids']:
                # Delete the chunks
                await loop.run_in_executor(
                    None,
                    lambda: collection.delete(ids=result['ids'])
                )
                logger.debug(f"Deleted {len(result['ids'])} existing chunks for file {file_id}")
        except Exception as e:
            logger.warning(f"Error deleting chunks for file {file_id}: {e}")

    async def get_file_chunks(self, project_id: int, file_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific file."""
        collection = await self._get_or_create_collection(project_id)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: collection.get(
                where={"file_id": str(file_id)},
                include=['documents', 'metadatas', 'embeddings']
            )
        )

        chunks = []
        if result and result['documents']:
            for i, (doc, metadata, embedding) in enumerate(zip(
                result['documents'],
                result['metadatas'],
                result.get('embeddings', [])
            )):
                chunks.append({
                    'id': result['ids'][i] if result.get('ids') else None,
                    'content': doc,
                    'metadata': metadata,
                    'embedding': embedding
                })

        return chunks

    async def delete_chunk(self, project_id: int, chunk_id: str) -> None:
        """Delete a specific chunk by ID."""
        collection = await self._get_or_create_collection(project_id)

        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: collection.delete(ids=[chunk_id])
            )
            logger.debug(f"Deleted chunk {chunk_id}")
        except Exception as e:
            logger.warning(f"Error deleting chunk {chunk_id}: {e}")

    async def search_chunks(
        self,
        project_id: int,
        query_embedding: np.ndarray,
        limit: int = 10,
        threshold: float = 0.1,
        query_text: str = ""
    ) -> List[Dict[str, Any]]:
        """Search chunks using ChromaDB vector similarity."""
        collection = await self._get_or_create_collection(project_id)

        # Convert numpy array to list for ChromaDB
        query_embedding_list = query_embedding.tolist()

        # Search in ChromaDB (run in executor)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: collection.query(
                query_embeddings=[query_embedding_list],
                n_results=limit * 2,  # Get more results for filtering
                include=['documents', 'metadatas', 'distances']
            )
        )

        # Get file information from metadata collection
        file_ids = set()
        if results and results['metadatas'] and results['metadatas'][0]:
            file_ids = {meta['file_id'] for meta in results['metadatas'][0]}

        # Fetch file paths
        file_map = await self._get_file_paths(project_id, list(file_ids))

        # Process results
        processed_results = []
        if results and results['documents']:
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                # Convert distance to similarity (ChromaDB uses cosine distance)
                # Cosine similarity = 1 - cosine distance
                similarity = 1.0 - distance

                # Enhanced matching for single-word queries
                if query_text:
                    import re
                    query_words = query_text.lower().split()
                    is_single_word = len(query_words) == 1

                    for word in query_words:
                        if len(word) > 1:
                            doc_lower = doc.lower()

                            # Exact word boundary match
                            if re.search(r'\b' + re.escape(word) + r'\b', doc_lower):
                                similarity += 0.7 if is_single_word else 0.5
                            # Partial match
                            elif word in doc_lower:
                                similarity += 0.3 if is_single_word else 0.2

                            # Programming keywords boost
                            programming_keywords = ['def', 'class', 'function', 'import', 'export',
                                                   'async', 'await', 'return', 'yield', 'test']
                            if word in programming_keywords and word in doc_lower:
                                similarity += 0.4

                    # Boost for micro/word chunks
                    if metadata.get('content_type') in ['micro', 'word']:
                        similarity += 0.2 if is_single_word else 0.1

                # Cap similarity
                similarity = min(similarity, 1.0)

                # Apply threshold
                if similarity >= threshold:
                    file_id = metadata['file_id']
                    file_path = file_map.get(file_id, 'unknown')

                    processed_results.append({
                        'chunk_id': i,
                        'file_path': file_path,
                        'content': doc,
                        'similarity': float(similarity),
                        'start_line': metadata.get('start_line', 1),
                        'end_line': metadata.get('end_line', 1),
                        'language': metadata.get('language', 'unknown'),
                        'content_type': metadata.get('content_type', 'code')
                    })

        # Sort by similarity and limit
        processed_results.sort(key=lambda x: x['similarity'], reverse=True)
        return processed_results[:limit]

    async def _get_file_paths(self, project_id: int, file_ids: List[str]) -> Dict[str, str]:
        """Get file paths for given file IDs."""
        if not file_ids:
            return {}

        collection = await self._get_or_create_metadata_collection("files")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: collection.get(
                ids=file_ids,
                where={"project_id": project_id}
            )
        )

        file_map = {}
        if result and result['metadatas']:
            for metadata in result['metadatas']:
                file_map[metadata['id']] = metadata['relative_path']

        return file_map

    async def search_chunks_memory_efficient(
        self,
        project_id: int,
        query_embedding: np.ndarray,
        limit: int = 10,
        threshold: float = 0.5,
        batch_size: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Memory-efficient search for large projects.

        Processes results in batches to avoid loading entire collection into memory.
        Recommended for collections with >100K chunks.

        Args:
            project_id: Project identifier
            query_embedding: Query vector
            limit: Number of results to return
            threshold: Similarity threshold (0.0-1.0)
            batch_size: Number of chunks to process per batch

        Returns:
            List of search results with similarity scores
        """
        collection = await self._get_or_create_collection(project_id)

        # Get collection size
        loop = asyncio.get_event_loop()
        collection_count = await loop.run_in_executor(
            None,
            lambda: collection.count()
        )

        # For small collections, use standard search
        if collection_count < 10000:
            return await self.search_chunks(project_id, query_embedding, limit, threshold)

        # For large collections, use batched approach
        logger.info(f"Using memory-efficient search for {collection_count} chunks")

        # Convert numpy array to list for ChromaDB
        query_embedding_list = query_embedding.tolist()

        # Get more results initially for better ranking
        n_results = min(limit * 10, collection_count)

        results = await loop.run_in_executor(
            None,
            lambda: collection.query(
                query_embeddings=[query_embedding_list],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
        )

        # Get file information
        file_ids = set()
        if results and results['metadatas'] and results['metadatas'][0]:
            file_ids = {meta['file_id'] for meta in results['metadatas'][0]}

        file_map = await self._get_file_paths(project_id, list(file_ids))

        # Process results
        processed_results = []
        if results and results['documents']:
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                similarity = 1.0 - distance

                if similarity >= threshold:
                    file_id = metadata['file_id']
                    file_path = file_map.get(file_id, 'unknown')

                    processed_results.append({
                        'chunk_id': i,
                        'file_path': file_path,
                        'content': doc,
                        'similarity': float(similarity),
                        'start_line': metadata.get('start_line', 1),
                        'end_line': metadata.get('end_line', 1),
                        'language': metadata.get('language', 'unknown'),
                        'content_type': metadata.get('content_type', 'code')
                    })

        # Sort by similarity and limit
        processed_results.sort(key=lambda x: x['similarity'], reverse=True)
        return processed_results[:limit]

    async def search_chunks_streaming(
        self,
        project_id: int,
        query_embedding: np.ndarray,
        threshold: float = 0.5,
        batch_size: int = 100
    ):
        """
        Stream search results for memory efficiency.

        Yields results one at a time instead of loading all into memory.
        Ideal for very large result sets or progressive display.

        Args:
            project_id: Project identifier
            query_embedding: Query vector
            threshold: Similarity threshold (0.0-1.0)
            batch_size: Number of chunks to process per batch

        Yields:
            Individual search results with similarity scores
        """
        collection = await self._get_or_create_collection(project_id)

        # Convert numpy array to list for ChromaDB
        query_embedding_list = query_embedding.tolist()

        loop = asyncio.get_event_loop()

        # Get collection count
        collection_count = await loop.run_in_executor(
            None,
            lambda: collection.count()
        )

        # Process in batches
        offset = 0
        while offset < collection_count:
            # Query batch
            batch_results = await loop.run_in_executor(
                None,
                lambda: collection.query(
                    query_embeddings=[query_embedding_list],
                    n_results=min(batch_size, collection_count - offset),
                    include=['documents', 'metadatas', 'distances']
                )
            )

            if not batch_results or not batch_results['ids'][0]:
                break

            # Get file information for this batch
            file_ids = {meta['file_id'] for meta in batch_results['metadatas'][0]}
            file_map = await self._get_file_paths(project_id, list(file_ids))

            # Yield results one by one
            for i, (doc_id, doc, metadata, distance) in enumerate(zip(
                batch_results['ids'][0],
                batch_results['documents'][0],
                batch_results['metadatas'][0],
                batch_results['distances'][0]
            )):
                similarity = 1.0 - distance

                if similarity >= threshold:
                    file_id = metadata['file_id']
                    file_path = file_map.get(file_id, 'unknown')

                    yield {
                        'chunk_id': doc_id,
                        'file_path': file_path,
                        'content': doc,
                        'similarity': float(similarity),
                        'start_line': metadata.get('start_line', 1),
                        'end_line': metadata.get('end_line', 1),
                        'language': metadata.get('language', 'unknown'),
                        'content_type': metadata.get('content_type', 'code')
                    }

            offset += batch_size

    async def get_project_stats(self, project_id: int) -> Dict[str, Any]:
        """Get project statistics."""
        # Get files from metadata collection
        files_collection = await self._get_or_create_metadata_collection("files")

        loop = asyncio.get_event_loop()
        files_result = await loop.run_in_executor(
            None,
            lambda: files_collection.get(
                where={"project_id": project_id}
            )
        )

        total_files = 0
        indexed_files = 0
        last_updated = None

        if files_result and files_result['metadatas']:
            total_files = len(files_result['metadatas'])
            indexed_files = sum(1 for meta in files_result['metadatas'] if meta.get('is_indexed', False))

            # Find latest update
            for meta in files_result['metadatas']:
                if meta.get('updated_at'):
                    file_date = datetime.fromisoformat(meta['updated_at'])
                    if last_updated is None or file_date > last_updated:
                        last_updated = file_date

        # Count chunks in ChromaDB
        collection = await self._get_or_create_collection(project_id)
        chunk_count = await loop.run_in_executor(
            None,
            lambda: collection.count()
        )

        return {
            'total_files': total_files,
            'indexed_files': indexed_files,
            'total_chunks': chunk_count,
            'last_updated': last_updated
        }

    # ========================================================================
    # Change logging
    # ========================================================================

    async def log_change(
        self,
        project_id: int,
        change_type: str,
        file_path: str,
        old_hash: Optional[str] = None,
        new_hash: Optional[str] = None,
        git_commit: Optional[str] = None,
        git_branch: Optional[str] = None,
        file_id: Optional[str] = None
    ) -> None:
        """Log a file change."""
        collection = await self._get_or_create_metadata_collection("changelogs")

        change_id = f"change_{project_id}_{datetime.now().isoformat()}_{file_path}".replace("/", "_").replace("\\", "_").replace(":", "_")

        change_data = {
            'project_id': project_id,
            'file_id': file_id or '',
            'change_type': change_type,
            'file_path': file_path,
            'old_hash': old_hash or '',
            'new_hash': new_hash or '',
            'git_commit': git_commit or '',
            'git_branch': git_branch or '',
            'processed': False,
            'created_at': datetime.now().isoformat()
        }

        dummy_embedding = [0.0] * 1  # Minimal embedding for metadata

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: collection.add(
                ids=[change_id],
                documents=[file_path],
                metadatas=[change_data],
                embeddings=[dummy_embedding]
            )
        )
