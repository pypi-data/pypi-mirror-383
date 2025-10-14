"""Vectorization engine for code processing and embedding generation."""

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import numpy as np
import tiktoken

# Lazy import: sentence-transformers is heavy and optional when using OpenAI provider
try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # ImportError or other issues
    SentenceTransformer = None  # type: ignore

from ..parsers.code_parser import CodeParser
from ..utils.text_utils import TextChunker, CodeChunker

logger = logging.getLogger(__name__)


class VectorizationEngine:
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        embedding_provider: str = "sentence-transformers",
        chunk_size: int = 256,
        chunk_overlap: int = 32,
        openai_api_key: Optional[str] = None
    ):
        self.embedding_model = embedding_model
        self.embedding_provider = embedding_provider
        self.chunk_size = min(chunk_size, 128)  # Force smaller chunks for better precision
        self.chunk_overlap = min(chunk_overlap, 16)
        self.openai_api_key = openai_api_key
        
        self._model = None
        self._tokenizer = None
        self.code_parser = CodeParser()
        self.text_chunker = TextChunker(chunk_size, chunk_overlap)
        self.code_chunker = CodeChunker(chunk_size, chunk_overlap)
    
    async def initialize(self):
        """Initialize the embedding model."""
        if self.embedding_provider == "sentence-transformers":
            # Lazy import in case module wasn't available at import time
            global SentenceTransformer  # type: ignore
            if SentenceTransformer is None:
                try:
                    import importlib
                    SentenceTransformer = importlib.import_module("sentence_transformers").SentenceTransformer  # type: ignore
                except Exception as e:
                    raise ImportError(
                        "sentence-transformers is required for 'sentence-transformers' provider.\n"
                        "Install it with: pip install sentence-transformers"
                    ) from e
            # Load in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(
                None, SentenceTransformer, self.embedding_model  # type: ignore[arg-type]
            )
        elif self.embedding_provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OpenAI API key required for OpenAI embeddings")
            # OpenAI client initialization would go here
            import openai
            openai.api_key = self.openai_api_key
        
        # Initialize tokenizer for token counting
        try:
            self._tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Could not initialize tokenizer: {e}")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error hashing file {file_path}: {e}")
            return ""
    
    async def process_file(
        self, 
        file_path: Path, 
        project_id: int, 
        file_id: int
    ) -> List[Dict[str, Any]]:
        """Process a single file and return chunks with embeddings."""
        try:
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    logger.error(f"Could not read file {file_path}: {e}")
                    return []
            
            # Detect language
            language = self._detect_language(file_path)
            
            # Parse code structure
            parsed_elements = await self.code_parser.parse_file(file_path, content)
            
            chunks = []
            chunk_index = 0
            
            # Process structured elements (functions, classes, etc.)
            for element in parsed_elements:
                element_chunks = await self._process_code_element(
                    element, project_id, file_id, language, chunk_index
                )
                chunks.extend(element_chunks)
                chunk_index += len(element_chunks)
            
            # Always add micro-chunks for better granularity, even if we have structured elements
            micro_chunks = await self._create_micro_chunks(content, project_id, file_id, language, len(chunks))
            chunks.extend(micro_chunks)
            
            # If no structured elements found, use code-aware chunking
            if len(chunks) == len(micro_chunks):  # Only micro chunks were added
                if language in ['python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'go', 'rust']:
                    text_chunks = self.code_chunker.chunk_code(content, language)
                else:
                    text_chunks = self.text_chunker.chunk_text(content)
                    
                for i, chunk_content in enumerate(text_chunks):
                    chunk_data = await self._create_chunk(
                        content=chunk_content,
                        project_id=project_id,
                        file_id=file_id,
                        chunk_index=len(chunks) + i,
                        content_type="code" if language != "text" else "text",
                        language=language,
                        start_line=self._estimate_start_line(chunk_content, content, i),
                        end_line=self._estimate_end_line(chunk_content, content, i)
                    )
                    chunks.append(chunk_data)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return []
    
    async def _process_code_element(
        self,
        element: Dict[str, Any],
        project_id: int,
        file_id: int,
        language: str,
        start_chunk_index: int
    ) -> List[Dict[str, Any]]:
        """Process a single code element (function, class, etc.)."""
        chunks = []
        content = element['content']
        
        # Check if content needs chunking
        if self._get_token_count(content) <= self.chunk_size:
            # Single chunk
            chunk_data = await self._create_chunk(
                content=content,
                project_id=project_id,
                file_id=file_id,
                chunk_index=start_chunk_index,
                content_type=element['type'],
                language=language,
                start_line=element['start_line'],
                end_line=element['end_line']
            )
            chunks.append(chunk_data)
        else:
            # Multiple chunks - use code-aware chunking for structured elements
            if language in ['python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'go', 'rust']:
                text_chunks = self.code_chunker.chunk_code(content, language)
            else:
                text_chunks = self.text_chunker.chunk_text(content)
                
            for i, chunk_content in enumerate(text_chunks):
                chunk_data = await self._create_chunk(
                    content=chunk_content,
                    project_id=project_id,
                    file_id=file_id,
                    chunk_index=start_chunk_index + i,
                    content_type=element['type'],
                    language=language,
                    start_line=element['start_line'],
                    end_line=element['end_line']
                )
                chunks.append(chunk_data)
        
        return chunks
    
    async def _create_chunk(
        self,
        content: str,
        project_id: int,
        file_id: int,
        chunk_index: int,
        content_type: str,
        language: str,
        start_line: int,
        end_line: int
    ) -> Dict[str, Any]:
        """Create a chunk with embedding."""
        # Generate embedding
        embedding = await self._generate_embedding(content)
        
        # Count tokens
        token_count = self._get_token_count(content)
        
        return {
            'project_id': project_id,
            'file_id': file_id,
            'chunk_index': chunk_index,
            'content': content,
            'content_type': content_type,
            'start_line': start_line,
            'end_line': end_line,
            'token_count': token_count,
            'language': language,
            'embedding': embedding.tolist() if embedding is not None else None,
            'embedding_model': self.embedding_model
        }
    
    async def _generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for text."""
        try:
            if self.embedding_provider == "sentence-transformers":
                # Run in executor to avoid blocking
                # Suppress progress bars to keep output clean
                loop = asyncio.get_event_loop()
                embedding = await loop.run_in_executor(
                    None, lambda: self._model.encode(text, show_progress_bar=False)
                )
                return embedding
            elif self.embedding_provider == "openai":
                # OpenAI embeddings implementation
                import openai
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: openai.Embedding.create(
                        input=text,
                        model=self.embedding_model
                    )
                )
                return np.array(response['data'][0]['embedding'])
            else:
                logger.error(f"Unknown embedding provider: {self.embedding_provider}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        extension = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.clj': 'clojure',
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'zsh',
            '.fish': 'fish',
            '.ps1': 'powershell',
            '.bat': 'batch',
            '.cmd': 'batch',
            '.md': 'markdown',
            '.txt': 'text',
            '.rst': 'restructuredtext',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.xml': 'xml',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.less': 'less',
            '.sql': 'sql',
            '.graphql': 'graphql',
            '.proto': 'protobuf'
        }
        
        return language_map.get(extension, 'text')
    
    def _get_token_count(self, text: str) -> int:
        """Get token count for text."""
        if self._tokenizer:
            try:
                return len(self._tokenizer.encode(text))
            except Exception:
                pass
        
        # Fallback: rough estimate (4 chars per token)
        return len(text) // 4
    
    async def generate_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """Generate embedding for a search query."""
        return await self._generate_embedding(query)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model."""
        if self.embedding_provider == "sentence-transformers" and self._model:
            return self._model.get_sentence_embedding_dimension()
        elif self.embedding_provider == "openai":
            # OpenAI text-embedding-ada-002 has 1536 dimensions
            if "ada-002" in self.embedding_model:
                return 1536
            else:
                return 1024  # Default for older models
        
        return 384  # Default fallback
    
    def _estimate_start_line(self, chunk_content: str, full_content: str, chunk_index: int) -> int:
        if chunk_index == 0:
            return 1
        
        # Find where this chunk starts in the full content
        chunk_start = full_content.find(chunk_content.strip()[:50])  # Use first 50 chars for matching
        if chunk_start == -1:
            return chunk_index * 10 + 1  # Rough estimate
        
        # Count newlines before this position
        lines_before = full_content[:chunk_start].count('\n')
        return lines_before + 1
    
    def _estimate_end_line(self, chunk_content: str, full_content: str, chunk_index: int) -> int:
        start_line = self._estimate_start_line(chunk_content, full_content, chunk_index)
        chunk_lines = chunk_content.count('\n') + 1
        return start_line + chunk_lines - 1
    
    async def _create_micro_chunks(self, content: str, project_id: int, file_id: int, language: str, start_index: int) -> List[Dict[str, Any]]:
        """Create very small chunks for better precision matching."""
        micro_chunks = []
        lines = content.split('\n')
        
        # Create chunks for individual lines that contain keywords
        keywords = ['test', 'def', 'class', 'function', 'import', 'from', 'async', 'await', 'return', 
                   'if', 'else', 'for', 'while', 'try', 'except', 'with', 'yield']
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('#') or line_stripped.startswith('//'):
                continue
                
            # Check if line contains any keywords or is a significant statement
            if (any(keyword in line_stripped.lower() for keyword in keywords) or 
                len(line_stripped) > 10):  # Non-trivial lines
                
                # Create context window around this line (3 lines total)
                start_line = max(0, i - 1)
                end_line = min(len(lines) - 1, i + 1)
                context_lines = lines[start_line:end_line + 1]
                context_content = '\n'.join(context_lines)
                
                if len(context_content.strip()) > 5:  # Skip very short contexts
                    chunk_data = await self._create_chunk(
                        content=context_content,
                        project_id=project_id,
                        file_id=file_id,
                        chunk_index=start_index + len(micro_chunks),
                        content_type="micro",
                        language=language,
                        start_line=start_line + 1,
                        end_line=end_line + 1
                    )
                    micro_chunks.append(chunk_data)
        
        # Also create word-level chunks for very specific matching
        word_chunks = await self._create_word_chunks(content, project_id, file_id, language, 
                                                     start_index + len(micro_chunks))
        micro_chunks.extend(word_chunks)
        
        return micro_chunks
    
    async def _create_word_chunks(self, content: str, project_id: int, file_id: int, language: str, start_index: int) -> List[Dict[str, Any]]:
        """Create word-level chunks for exact matching."""
        word_chunks = []
        
        # Extract significant words and their contexts
        import re
        words = re.findall(r'\b\w{3,}\b', content.lower())  # Words with 3+ characters
        unique_words = list(set(words))
        
        # Focus on programming-related words
        programming_words = ['test', 'function', 'class', 'method', 'import', 'export', 
                            'async', 'await', 'return', 'yield', 'def', 'var', 'let', 'const']
        
        for word in programming_words:
            if word in unique_words:
                # Find all occurrences of this word with context
                pattern = re.compile(r'.{0,50}\b' + re.escape(word) + r'\b.{0,50}', re.IGNORECASE)
                matches = pattern.findall(content)
                
                for i, match in enumerate(matches[:3]):  # Limit to 3 occurrences per word
                    if len(match.strip()) > 10:
                        chunk_data = await self._create_chunk(
                            content=match.strip(),
                            project_id=project_id,
                            file_id=file_id,
                            chunk_index=start_index + len(word_chunks),
                            content_type="word",
                            language=language,
                            start_line=1,  # Approximate
                            end_line=1
                        )
                        word_chunks.append(chunk_data)
        
        return word_chunks
