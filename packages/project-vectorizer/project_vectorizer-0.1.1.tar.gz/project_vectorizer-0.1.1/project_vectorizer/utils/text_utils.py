"""Text processing utilities for chunking and tokenization."""

import re
from typing import List, Tuple


class TextChunker:
    """Utility for chunking text into smaller pieces."""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        if not text.strip():
            return []
        
        # First try to chunk by natural boundaries
        chunks = self._chunk_by_paragraphs(text)
        
        # If chunks are still too large, split them further
        final_chunks = []
        for chunk in chunks:
            if self._estimate_token_count(chunk) <= self.chunk_size:
                final_chunks.append(chunk)
            else:
                final_chunks.extend(self._chunk_by_sentences(chunk))
        
        return [chunk.strip() for chunk in final_chunks if chunk.strip()]
    
    def _chunk_by_paragraphs(self, text: str) -> List[str]:
        """Chunk text by paragraphs."""
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if adding this paragraph would exceed chunk size
            potential_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if self._estimate_token_count(potential_chunk) <= self.chunk_size:
                current_chunk = potential_chunk
            else:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """Chunk text by sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding this sentence would exceed chunk size
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if self._estimate_token_count(potential_chunk) <= self.chunk_size:
                current_chunk = potential_chunk
            else:
                # Save current chunk and start new one with overlap
                if current_chunk:
                    chunks.append(current_chunk)
                    # Create overlap by taking last few sentences
                    overlap_sentences = self._get_overlap_sentences(current_chunk)
                    current_chunk = overlap_sentences + " " + sentence if overlap_sentences else sentence
                else:
                    # Single sentence is too large, split by words
                    chunks.extend(self._chunk_by_words(sentence))
                    current_chunk = ""
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _chunk_by_words(self, text: str) -> List[str]:
        """Chunk text by words as last resort."""
        words = text.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            potential_chunk = current_chunk + " " + word if current_chunk else word
            
            if self._estimate_token_count(potential_chunk) <= self.chunk_size:
                current_chunk = potential_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    # Create overlap
                    overlap_words = current_chunk.split()[-self.overlap//4:]  # Rough overlap
                    current_chunk = " ".join(overlap_words) + " " + word
                else:
                    # Single word is too large (shouldn't happen often)
                    chunks.append(word)
                    current_chunk = ""
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _get_overlap_sentences(self, chunk: str) -> str:
        """Get last few sentences for overlap."""
        sentences = re.split(r'(?<=[.!?])\s+', chunk)
        if len(sentences) <= 1:
            return ""
        
        # Take last 1-2 sentences for overlap, ensuring we don't exceed overlap limit
        overlap_sentences = []
        current_length = 0
        
        for sentence in reversed(sentences):
            sentence_length = self._estimate_token_count(sentence)
            if current_length + sentence_length <= self.overlap:
                overlap_sentences.insert(0, sentence)
                current_length += sentence_length
            else:
                break
        
        return " ".join(overlap_sentences)
    
    def _estimate_token_count(self, text: str) -> int:
        """Rough estimate of token count."""
        # Simple approximation: 4 characters per token
        return len(text) // 4


class CodeChunker(TextChunker):
    """Specialized chunker for code that respects code structure."""
    
    def chunk_code(self, code: str, language: str = "python") -> List[str]:
        """Chunk code while trying to preserve structure."""
        if language == "python":
            return self._chunk_python_code(code)
        elif language in ["javascript", "typescript", "java", "cpp", "c"]:
            return self._chunk_brace_based_code(code)
        else:
            # Fall back to regular text chunking
            return self.chunk_text(code)
    
    def _chunk_python_code(self, code: str) -> List[str]:
        """Chunk Python code by respecting indentation."""
        lines = code.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a function or class definition
            if re.match(r'^\s*(def|class|async\s+def)\s+', line):
                # Find the end of this function/class
                indent_level = len(line) - len(line.lstrip())
                block_lines = [line]
                block_size = self._estimate_token_count(line)
                
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if next_line.strip() == '':
                        block_lines.append(next_line)
                        j += 1
                        continue
                    
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent_level and next_line.strip():
                        break
                    
                    block_lines.append(next_line)
                    block_size += self._estimate_token_count(next_line)
                    j += 1
                
                # Check if this block fits in current chunk
                if current_size + block_size <= self.chunk_size:
                    current_chunk.extend(block_lines)
                    current_size += block_size
                else:
                    # Save current chunk and start new one
                    if current_chunk:
                        chunks.append('\n'.join(current_chunk))
                    current_chunk = block_lines
                    current_size = block_size
                
                i = j
            else:
                # Regular line
                line_size = self._estimate_token_count(line)
                if current_size + line_size <= self.chunk_size:
                    current_chunk.append(line)
                    current_size += line_size
                else:
                    # Save current chunk and start new one
                    if current_chunk:
                        chunks.append('\n'.join(current_chunk))
                    current_chunk = [line]
                    current_size = line_size
                
                i += 1
        
        # Add the last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    
    def _chunk_brace_based_code(self, code: str) -> List[str]:
        """Chunk code that uses braces for blocks."""
        lines = code.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        brace_level = 0
        
        for line in lines:
            line_size = self._estimate_token_count(line)
            
            # Count braces to track nesting level
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            # Check if adding this line would exceed chunk size
            if current_size + line_size <= self.chunk_size:
                current_chunk.append(line)
                current_size += line_size
                brace_level += open_braces - close_braces
            else:
                # If we're at the top level, we can create a new chunk
                if brace_level == 0 and current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = [line]
                    current_size = line_size
                    brace_level = open_braces - close_braces
                else:
                    # We're in the middle of a block, add line anyway
                    current_chunk.append(line)
                    current_size += line_size
                    brace_level += open_braces - close_braces
        
        # Add the last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return [chunk.strip() for chunk in chunks if chunk.strip()]


def clean_text(text: str) -> str:
    """Clean text by removing excessive whitespace and normalizing."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_comments_and_docstrings(code: str, language: str) -> Tuple[str, str]:
    """Extract comments and docstrings separately from code."""
    comments = []
    clean_code = code
    
    if language == "python":
        # Extract docstrings
        docstring_pattern = r'(""".*?"""|\'\'\'.*?\'\'\')'
        docstrings = re.findall(docstring_pattern, code, re.DOTALL)
        
        # Extract comments
        comment_pattern = r'#.*?$'
        code_comments = re.findall(comment_pattern, code, re.MULTILINE)
        
        comments.extend(code_comments)
        comments.extend(docstrings)
        
        # Remove comments from code
        clean_code = re.sub(docstring_pattern, '', code, flags=re.DOTALL)
        clean_code = re.sub(comment_pattern, '', clean_code, flags=re.MULTILINE)
    
    elif language in ["javascript", "typescript", "java", "cpp", "c"]:
        # Extract multi-line comments
        multiline_pattern = r'/\*.*?\*/'
        multiline_comments = re.findall(multiline_pattern, code, re.DOTALL)
        
        # Extract single-line comments
        singleline_pattern = r'//.*?$'
        singleline_comments = re.findall(singleline_pattern, code, re.MULTILINE)
        
        comments.extend(multiline_comments)
        comments.extend(singleline_comments)
        
        # Remove comments from code
        clean_code = re.sub(multiline_pattern, '', code, flags=re.DOTALL)
        clean_code = re.sub(singleline_pattern, '', clean_code, flags=re.MULTILINE)
    
    # Clean up the results
    comments_text = '\n'.join(comments).strip()
    clean_code = clean_text(clean_code)
    
    return clean_code, comments_text