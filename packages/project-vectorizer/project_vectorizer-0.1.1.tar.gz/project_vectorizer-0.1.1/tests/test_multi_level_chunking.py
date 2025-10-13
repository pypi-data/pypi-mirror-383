"""Tests for multi-level chunking functionality."""

import asyncio
import pytest
from pathlib import Path
from typing import Dict, List, Any

from project_vectorizer.vectorizer.engine import VectorizationEngine


class TestMultiLevelChunking:
    """Test multi-level chunking capabilities."""

    @pytest.mark.asyncio
    async def test_function_and_class_chunking(self, sample_python_file: Path):
        """Test that functions and classes are properly chunked."""
        engine = VectorizationEngine(chunk_size=128, chunk_overlap=16)
        await engine.initialize()
        
        chunks = await engine.process_file(sample_python_file, project_id=1, file_id=1)
        
        # Should generate multiple chunks
        assert len(chunks) > 0, "Should generate chunks from sample file"
        
        # Categorize chunks by type
        chunk_types = {}
        for chunk in chunks:
            content_type = chunk['content_type']
            if content_type not in chunk_types:
                chunk_types[content_type] = []
            chunk_types[content_type].append(chunk)
        
        # Should have function chunks
        assert 'function' in chunk_types, f"Should have function chunks. Got types: {list(chunk_types.keys())}"
        
        # Should have micro chunks
        assert 'micro' in chunk_types, f"Should have micro chunks. Got types: {list(chunk_types.keys())}"
        
        # Should have word chunks
        assert 'word' in chunk_types, f"Should have word chunks. Got types: {list(chunk_types.keys())}"
        
        # Verify function chunks contain actual function content
        function_chunks = chunk_types['function']
        assert len(function_chunks) > 0, "Should have at least one function chunk"
        
        # At least one function chunk should contain 'def' or 'async def'
        function_content = [chunk['content'] for chunk in function_chunks]
        has_function_definition = any('def ' in content for content in function_content)
        assert has_function_definition, "Function chunks should contain function definitions"

    @pytest.mark.asyncio
    async def test_micro_chunk_generation(self, temp_dir: Path):
        """Test that micro chunks are generated for important statements."""
        # Create test file with various programming constructs
        test_file = temp_dir / "micro_test.py"
        test_file.write_text("""
#!/usr/bin/env python3
'''Test file for micro chunking.'''

import os
import sys
from pathlib import Path

def main():
    '''Main function.'''
    print("Starting application")
    
    if __name__ == "__main__":
        result = process_data()
        return result

async def process_data():
    '''Process data asynchronously.'''
    try:
        data = await load_data()
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

class DataProcessor:
    '''Process data efficiently.'''
    
    def __init__(self):
        self.data = []
        self.processed = False

for item in range(10):
    print(f"Item: {item}")
    
while True:
    break
    
with open("test.txt", "r") as f:
    content = f.read()
""")
        
        engine = VectorizationEngine(chunk_size=64, chunk_overlap=8)
        await engine.initialize()
        
        chunks = await engine.process_file(test_file, project_id=1, file_id=1)
        
        # Filter micro chunks
        micro_chunks = [chunk for chunk in chunks if chunk['content_type'] == 'micro']
        
        assert len(micro_chunks) > 0, "Should generate micro chunks"
        
        # Micro chunks should contain important keywords
        micro_content = ' '.join(chunk['content'] for chunk in micro_chunks)
        important_keywords = ['import', 'def', 'class', 'if', 'for', 'while', 'try', 'with', 'async']
        
        found_keywords = [kw for kw in important_keywords if kw in micro_content.lower()]
        assert len(found_keywords) > 0, f"Micro chunks should contain important keywords. Found: {found_keywords}"

    @pytest.mark.asyncio  
    async def test_word_chunk_generation(self, temp_dir: Path):
        """Test that word-level chunks are generated for programming terms."""
        # Create test file with specific programming terms
        test_file = temp_dir / "word_test.py"
        test_file.write_text("""
# File with various programming terms
import asyncio
from typing import List, Dict

async def test_function():
    '''Function for testing word chunking.'''
    return "test result"

def helper_function():
    '''Helper function implementation.'''
    pass

class TestClass:
    '''Test class definition.'''
    
    def method_test(self):
        '''Test method implementation.'''
        return True

# Variables with programming terms
function_name = "test_function"
class_instance = TestClass()
async_result = await test_function()
""")
        
        engine = VectorizationEngine(chunk_size=64, chunk_overlap=8)
        await engine.initialize()
        
        chunks = await engine.process_file(test_file, project_id=1, file_id=1)
        
        # Filter word chunks
        word_chunks = [chunk for chunk in chunks if chunk['content_type'] == 'word']
        
        assert len(word_chunks) > 0, "Should generate word chunks"
        
        # Word chunks should focus on programming keywords
        word_content = ' '.join(chunk['content'] for chunk in word_chunks)
        programming_words = ['test', 'function', 'class', 'async', 'import', 'def']
        
        found_words = [word for word in programming_words if word in word_content.lower()]
        assert len(found_words) > 0, f"Word chunks should contain programming terms. Found: {found_words}"

    @pytest.mark.asyncio
    async def test_chunk_size_respect(self, sample_python_file: Path):
        """Test that chunks respect the specified size limits."""
        engine = VectorizationEngine(chunk_size=64, chunk_overlap=8)
        await engine.initialize()
        
        chunks = await engine.process_file(sample_python_file, project_id=1, file_id=1)
        
        # Check token counts
        oversized_chunks = []
        for chunk in chunks:
            token_count = chunk.get('token_count', 0)
            if token_count > 64:  # Allow some tolerance for exact matches
                oversized_chunks.append(chunk)
        
        # Most chunks should be within size limits
        oversized_ratio = len(oversized_chunks) / len(chunks)
        assert oversized_ratio < 0.1, f"Too many oversized chunks: {oversized_ratio:.2%}"

    @pytest.mark.asyncio
    async def test_javascript_chunking(self, sample_js_file: Path):
        """Test chunking of JavaScript files."""
        engine = VectorizationEngine(chunk_size=128, chunk_overlap=16)
        await engine.initialize()
        
        chunks = await engine.process_file(sample_js_file, project_id=1, file_id=1)
        
        assert len(chunks) > 0, "Should generate chunks from JavaScript file"
        
        # Should detect JavaScript language
        js_chunks = [chunk for chunk in chunks if chunk['language'] == 'javascript']
        assert len(js_chunks) > 0, "Should detect JavaScript language"
        
        # Should contain JavaScript-specific content
        all_content = ' '.join(chunk['content'] for chunk in chunks)
        js_keywords = ['const', 'function', 'class', 'require', 'module.exports', 'async']
        
        found_js_keywords = [kw for kw in js_keywords if kw in all_content]
        assert len(found_js_keywords) > 0, f"Should find JavaScript keywords. Found: {found_js_keywords}"

    @pytest.mark.asyncio
    async def test_chunk_overlap(self, temp_dir: Path):
        """Test that chunk overlap works correctly."""
        # Create test file with continuous content
        test_file = temp_dir / "overlap_test.py"
        test_file.write_text("""
# This is a continuous piece of code for testing overlap functionality
# Line 1: First line of content
# Line 2: Second line of content  
# Line 3: Third line of content
# Line 4: Fourth line of content
# Line 5: Fifth line of content
# Line 6: Sixth line of content
# Line 7: Seventh line of content
# Line 8: Eighth line of content

def function_one():
    '''First function implementation.'''
    return "first result"

def function_two():
    '''Second function implementation.'''
    return "second result"

def function_three():
    '''Third function implementation.'''
    return "third result"
""")
        
        engine = VectorizationEngine(chunk_size=32, chunk_overlap=8)
        await engine.initialize()
        
        chunks = await engine.process_file(test_file, project_id=1, file_id=1)
        
        # Should generate multiple chunks due to small chunk size
        assert len(chunks) > 3, "Should generate multiple chunks with small chunk size"
        
        # Check that some content appears in multiple chunks (overlap)
        all_contents = [chunk['content'] for chunk in chunks]
        
        # Find overlapping content by checking for common substrings
        overlaps_found = 0
        for i in range(len(all_contents) - 1):
            content1 = all_contents[i].strip()
            content2 = all_contents[i + 1].strip()
            
            # Check for any common lines or phrases
            lines1 = set(content1.split('\n'))
            lines2 = set(content2.split('\n'))
            
            if lines1.intersection(lines2):
                overlaps_found += 1
        
        # Should have some overlapping content
        assert overlaps_found > 0, "Should find overlapping content between chunks"

    @pytest.mark.asyncio
    async def test_embedding_generation(self, temp_dir: Path):
        """Test that embeddings are generated for all chunk types."""
        test_file = temp_dir / "embedding_test.py"
        test_file.write_text("""
def test_function():
    '''Test embedding generation.'''
    return "test"

class TestClass:
    '''Test class for embeddings.'''
    pass
""")
        
        engine = VectorizationEngine(chunk_size=64, chunk_overlap=8)
        await engine.initialize()
        
        chunks = await engine.process_file(test_file, project_id=1, file_id=1)
        
        # All chunks should have embeddings
        chunks_without_embeddings = [chunk for chunk in chunks if chunk['embedding'] is None]
        
        assert len(chunks_without_embeddings) == 0, \
            f"All chunks should have embeddings. {len(chunks_without_embeddings)} chunks missing embeddings"
        
        # Embeddings should be arrays of reasonable length
        for chunk in chunks:
            embedding = chunk['embedding']
            assert isinstance(embedding, list), "Embedding should be a list"
            assert len(embedding) > 0, "Embedding should not be empty"
            assert len(embedding) >= 300, f"Embedding seems too short: {len(embedding)} dimensions"

    @pytest.mark.asyncio
    async def test_line_number_tracking(self, temp_dir: Path):
        """Test that line numbers are properly tracked in chunks."""
        test_file = temp_dir / "line_test.py"
        test_content = """# Line 1
# Line 2 
# Line 3

def function_at_line_5():
    '''Function starting at line 5.'''
    return "line 7 content"

# Line 9
class ClassAtLine10:
    '''Class starting at line 10.'''
    
    def method_at_line_12(self):
        '''Method at line 12.'''
        pass

# Line 16
# Line 17
"""
        test_file.write_text(test_content)
        
        engine = VectorizationEngine(chunk_size=64, chunk_overlap=8)
        await engine.initialize()
        
        chunks = await engine.process_file(test_file, project_id=1, file_id=1)
        
        # All chunks should have line numbers
        for chunk in chunks:
            assert 'start_line' in chunk, "Chunk should have start_line"
            assert 'end_line' in chunk, "Chunk should have end_line"
            assert chunk['start_line'] > 0, "Start line should be positive"
            assert chunk['end_line'] >= chunk['start_line'], "End line should be >= start line"

    @pytest.mark.asyncio
    async def test_chunk_content_quality(self, sample_python_file: Path):
        """Test that chunk content is meaningful and well-formed."""
        engine = VectorizationEngine(chunk_size=128, chunk_overlap=16)
        await engine.initialize()
        
        chunks = await engine.process_file(sample_python_file, project_id=1, file_id=1)
        
        # Check content quality
        empty_chunks = [chunk for chunk in chunks if not chunk['content'].strip()]
        assert len(empty_chunks) == 0, "Should not have empty chunks"
        
        # Chunks should have reasonable length
        very_short_chunks = [chunk for chunk in chunks if len(chunk['content']) < 5]
        short_ratio = len(very_short_chunks) / len(chunks)
        assert short_ratio < 0.1, f"Too many very short chunks: {short_ratio:.2%}"
        
        # Function chunks should contain proper function syntax
        function_chunks = [chunk for chunk in chunks if chunk['content_type'] == 'function']
        for func_chunk in function_chunks:
            content = func_chunk['content']
            # Should contain either 'def ' or 'async def ' for Python functions
            has_function_def = 'def ' in content or 'class ' in content
            assert has_function_def, f"Function chunk should contain function definition: {content[:100]}"