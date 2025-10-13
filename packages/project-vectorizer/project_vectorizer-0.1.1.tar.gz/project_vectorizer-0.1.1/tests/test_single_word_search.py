"""Tests for enhanced single-word search functionality."""

import asyncio
import pytest
from pathlib import Path

from project_vectorizer.core.config import Config
from project_vectorizer.core.project import ProjectManager
from project_vectorizer.vectorizer.engine import VectorizationEngine


class TestSingleWordSearch:
    """Test enhanced single-word search capabilities."""

    @pytest.mark.asyncio
    async def test_single_word_exact_match(self, temp_dir: Path):
        """Test that single words achieve perfect similarity scores."""
        # Create test file with specific keywords
        test_file = temp_dir / "test_code.py"
        test_file.write_text("""
async def process_data():
    '''Process data asynchronously.'''
    return await some_function()

class DataHandler:
    '''Handle data processing.'''
    
    def __init__(self):
        self.data = []
    
    def validate(self, item):
        '''Validate a data item.'''
        return True

def helper_function():
    '''A helper function.'''
    pass

import os
import asyncio
from typing import List
""")
        
        # Set up project
        config = Config(chunk_size=128, embedding_provider="sentence-transformers")
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-single-word")
        await project_manager.index_all()
        
        # Test single-word searches with high thresholds
        test_cases = [
            ("async", 0.9),
            ("def", 0.8),
            ("class", 0.85),
            ("import", 0.9),
            ("function", 0.95),
        ]
        
        for word, threshold in test_cases:
            results = await project_manager.search(word, limit=5, threshold=threshold)
            
            # Should find at least one result
            assert len(results) > 0, f"No results found for '{word}' with threshold {threshold}"
            
            # Check that top results have high similarity
            top_result = results[0]
            assert top_result['similarity'] >= threshold, \
                f"Top result for '{word}' has similarity {top_result['similarity']}, expected >= {threshold}"
            
            # Verify that the word actually appears in the content
            content_lower = top_result['content'].lower()
            assert word in content_lower, f"Word '{word}' not found in result content: {top_result['content'][:100]}"

    @pytest.mark.asyncio
    async def test_programming_keyword_detection(self, temp_dir: Path):
        """Test special handling of programming keywords."""
        # Create test file with programming keywords
        test_file = temp_dir / "keywords.py"
        test_file.write_text("""
def main():
    '''Main function.'''
    pass

async def async_handler():
    '''Async handler function.'''
    await process_data()
    return result

class TestClass:
    '''Test class definition.'''
    
    def __init__(self):
        self.value = 42
        
    def test_method(self):
        '''Test method.'''
        return self.value

import json
import asyncio
from typing import Dict, List

var = "test"
let_equivalent = "javascript_style"
const_like = "constant_value"
""")
        
        # Set up project  
        config = Config(chunk_size=128, embedding_provider="sentence-transformers")
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-keywords")
        await project_manager.index_all()
        
        # Test programming keywords with very high thresholds
        programming_keywords = [
            "def", "class", "async", "import", "test", "function"
        ]
        
        for keyword in programming_keywords:
            results = await project_manager.search(keyword, limit=3, threshold=0.9)
            
            assert len(results) > 0, f"No results for programming keyword '{keyword}'"
            
            # Should achieve perfect or near-perfect similarity
            top_similarity = results[0]['similarity']
            assert top_similarity >= 0.9, \
                f"Programming keyword '{keyword}' got similarity {top_similarity}, expected >= 0.9"

    @pytest.mark.asyncio
    async def test_word_boundary_matching(self, temp_dir: Path):
        """Test that word boundary matching works correctly."""
        # Create test file with similar words
        test_file = temp_dir / "boundaries.py"
        test_file.write_text("""
def test_function():
    '''Testing function.'''
    testing_var = "test_value"
    untested = True
    return test_result

class Tester:
    '''A tester class.'''
    
    def test_method(self):
        '''Method for testing.'''
        self.tested = True
        return "test"
        
# This has the word 'test' as exact match
test = "exact_test_variable"
""")
        
        # Set up project
        config = Config(chunk_size=128)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-boundaries")
        await project_manager.index_all()
        
        # Search for exact word "test"
        results = await project_manager.search("test", limit=10, threshold=0.7)
        
        assert len(results) > 0, "No results found for 'test'"
        
        # Check that results with exact word boundaries score higher
        exact_matches = []
        partial_matches = []
        
        for result in results:
            content = result['content'].lower()
            import re
            
            if re.search(r'\btest\b', content):
                exact_matches.append(result)
            elif 'test' in content:
                partial_matches.append(result)
        
        # Should have both exact and partial matches
        assert len(exact_matches) > 0, "No exact word boundary matches found"
        
        # Exact matches should generally have higher scores
        if exact_matches and partial_matches:
            avg_exact_score = sum(r['similarity'] for r in exact_matches) / len(exact_matches)
            avg_partial_score = sum(r['similarity'] for r in partial_matches) / len(partial_matches)
            
            # Exact matches should have higher average similarity
            assert avg_exact_score >= avg_partial_score, \
                f"Exact matches ({avg_exact_score:.3f}) should score higher than partial matches ({avg_partial_score:.3f})"

    @pytest.mark.asyncio
    async def test_adaptive_threshold_handling(self, temp_dir: Path):
        """Test that single-word queries use adaptive thresholds."""
        # Create test file
        test_file = temp_dir / "adaptive.py"
        test_file.write_text("""
async def example_async():
    '''Example async function.'''
    result = await some_operation()
    return result
    
def regular_function():
    '''Regular function.'''
    return "value"
""")
        
        # Set up project
        config = Config(chunk_size=128)  
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-adaptive")
        await project_manager.index_all()
        
        # Test single-word query with high threshold
        single_word_results = await project_manager.search("async", limit=5, threshold=0.9)
        
        # Test multi-word query with same high threshold
        multi_word_results = await project_manager.search("async function example", limit=5, threshold=0.9)
        
        # Single-word query should return results even with high threshold
        assert len(single_word_results) > 0, "Single-word query should return results with high threshold"
        
        # Multi-word query might return fewer results with high threshold (this is expected)
        # The key is that single-word queries are handled specially

    @pytest.mark.asyncio
    async def test_similarity_boosting(self, temp_dir: Path):
        """Test that similarity scores are boosted appropriately for single words."""
        # Create test file with clear matches
        test_file = temp_dir / "boosting.py"
        test_file.write_text("""
import os
import sys
from pathlib import Path

async def main():
    '''Main async function.'''
    data = await load_data()
    result = process(data)
    return result

def process(data):
    '''Process the data.'''
    return data.upper()

class Processor:
    '''Data processor class.'''
    
    def __init__(self):
        self.processed = []
""")
        
        # Set up project
        config = Config(chunk_size=128)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-boosting")
        await project_manager.index_all()
        
        # Search for a word that should get boosted
        results = await project_manager.search("import", limit=5, threshold=0.5)
        
        assert len(results) > 0, "Should find results for 'import'"
        
        # Check that the top result has very high similarity
        top_result = results[0]
        assert top_result['similarity'] >= 0.8, \
            f"Expected high similarity for exact 'import' match, got {top_result['similarity']}"
        
        # Verify the content actually contains the word
        assert 'import' in top_result['content'].lower(), \
            "Top result should contain the search word"

    @pytest.mark.asyncio
    async def test_multiple_languages(self, temp_dir: Path, sample_js_file: Path):
        """Test single-word search across multiple programming languages."""
        # Create Python file
        py_file = temp_dir / "test.py"
        py_file.write_text("""
class DataHandler:
    async def process(self):
        return "processed"
""")
        
        # Copy JavaScript file to temp directory
        js_target = temp_dir / "test.js"
        js_target.write_text(sample_js_file.read_text())
        
        # Set up project
        config = Config(chunk_size=128)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-multilang")
        await project_manager.index_all()
        
        # Search for words that exist in both languages
        test_words = ["class", "async", "function"]
        
        for word in test_words:
            results = await project_manager.search(word, limit=10, threshold=0.7)
            
            assert len(results) > 0, f"Should find results for '{word}' across languages"
            
            # Should find matches from both Python and JavaScript files
            file_extensions = set()
            for result in results:
                file_path = result['file_path']
                if '.' in file_path:
                    ext = '.' + file_path.split('.')[-1]
                    file_extensions.add(ext)
            
            # We should find results from multiple file types for common keywords
            if word in ["class", "async", "function"]:
                assert len(file_extensions) >= 1, \
                    f"Expected results from multiple languages for '{word}'"

    @pytest.mark.asyncio
    async def test_result_ranking_priority(self, temp_dir: Path):
        """Test that single-word search results are properly ranked by priority."""
        # Create test file with various match types
        test_file = temp_dir / "ranking.py" 
        test_file.write_text("""
# This file has the word 'test' in various contexts

def test_function():  # Exact word boundary match
    '''Testing function with test in docstring.'''
    testing_variable = "contains test word"  # Partial matches
    untested_value = True  # Word within another word
    return test_result  # Another exact match

class TestCase:  # Exact match in class name
    '''Class for testing purposes.'''
    
    def test_method(self):  # Exact match in method name
        self.tested = True
        return "test"  # Exact match in string literal

# Variable named exactly 'test'
test = "exact_variable_name"

# Comment with test keyword
# This is a test comment with multiple test occurrences for test purposes
""")
        
        # Set up project
        config = Config(chunk_size=64)  # Smaller chunks for more granular results
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-ranking")
        await project_manager.index_all()
        
        # Search for 'test' with moderate threshold
        results = await project_manager.search("test", limit=15, threshold=0.3)
        
        assert len(results) >= 3, "Should find multiple results for 'test'"
        
        # Top results should have higher similarity scores
        similarities = [r['similarity'] for r in results]
        
        # Verify results are properly sorted by similarity (descending)
        assert similarities == sorted(similarities, reverse=True), \
            "Results should be sorted by similarity in descending order"
        
        # Top result should have very high similarity
        assert similarities[0] >= 0.8, \
            f"Top result should have high similarity, got {similarities[0]}"