"""Tests for complete end-to-end workflow functionality."""

import asyncio
import pytest
from pathlib import Path

from project_vectorizer.core.config import Config
from project_vectorizer.core.project import ProjectManager


class TestCompleteWorkflow:
    """Test complete end-to-end workflow."""

    @pytest.mark.asyncio
    async def test_init_index_search_workflow(self, temp_dir: Path):
        """Test complete workflow: init -> index -> search."""
        # Create sample files
        py_file = temp_dir / "main.py"
        py_file.write_text("""
import asyncio
import json
from typing import List, Dict

async def main():
    '''Main application entry point.'''
    data = await load_data()
    result = await process_data(data)
    return result

async def load_data() -> List[Dict]:
    '''Load data from source.'''
    return [
        {'id': 1, 'name': 'test_item', 'type': 'sample'},
        {'id': 2, 'name': 'demo_item', 'type': 'example'}
    ]

async def process_data(items: List[Dict]) -> Dict:
    '''Process the loaded data.'''
    processed = []
    for item in items:
        if validate_item(item):
            processed.append(item)
    
    return {
        'total': len(items),
        'processed': len(processed),
        'items': processed
    }

def validate_item(item: Dict) -> bool:
    '''Validate a data item.'''
    required_fields = ['id', 'name', 'type']
    return all(field in item for field in required_fields)

class DataHandler:
    '''Handle data operations.'''
    
    def __init__(self):
        self.cache = {}
    
    async def get_item(self, item_id: int) -> Dict:
        '''Get item by ID.'''
        if item_id in self.cache:
            return self.cache[item_id]
        
        # Simulate async data fetch
        await asyncio.sleep(0.01)
        item = {'id': item_id, 'fetched': True}
        self.cache[item_id] = item
        return item

if __name__ == "__main__":
    asyncio.run(main())
""")
        
        js_file = temp_dir / "utils.js"
        js_file.write_text("""
// Utility functions for data processing
const fs = require('fs');
const path = require('path');

class DataProcessor {
    constructor() {
        this.processed = [];
        this.errors = [];
    }
    
    async processFile(filePath) {
        try {
            const data = await this.readFile(filePath);
            const result = this.transformData(data);
            this.processed.push(result);
            return result;
        } catch (error) {
            this.errors.push(error);
            throw error;
        }
    }
    
    readFile(filePath) {
        return new Promise((resolve, reject) => {
            fs.readFile(filePath, 'utf8', (err, data) => {
                if (err) reject(err);
                else resolve(data);
            });
        });
    }
    
    transformData(rawData) {
        try {
            const parsed = JSON.parse(rawData);
            return {
                ...parsed,
                transformed: true,
                timestamp: Date.now()
            };
        } catch (error) {
            return {
                raw: rawData,
                transformed: false,
                error: error.message
            };
        }
    }
    
    getStats() {
        return {
            processed: this.processed.length,
            errors: this.errors.length,
            success_rate: this.processed.length / (this.processed.length + this.errors.length)
        };
    }
}

function validateConfig(config) {
    const required = ['host', 'port', 'database'];
    const missing = required.filter(key => !config[key]);
    
    if (missing.length > 0) {
        throw new Error(`Missing required config: ${missing.join(', ')}`);
    }
    
    return true;
}

async function connectDatabase(config) {
    validateConfig(config);
    
    // Simulate connection
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return {
        connected: true,
        host: config.host,
        database: config.database
    };
}

module.exports = {
    DataProcessor,
    validateConfig,
    connectDatabase
};
""")
        
        # Step 1: Initialize project
        config = Config(chunk_size=128, embedding_model="all-MiniLM-L6-v2")
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-workflow")
        
        # Verify initialization
        assert project_manager.project is not None, "Project should be initialized"
        assert project_manager.project.name == "test-workflow"
        
        # Step 2: Index the project
        await project_manager.index_all()
        
        # Verify indexing
        status = await project_manager.get_status()
        assert status['total_files'] >= 2, "Should have indexed at least 2 files"
        assert status['indexed_files'] >= 2, "Should have indexed at least 2 files"
        assert status['total_chunks'] > 0, "Should have generated chunks"
        
        # Step 3: Test searches
        # Note: Similarity scores may vary based on embedding model and chunking
        search_tests = [
            ("async", 0.6, "Should find async functions"),
            ("class", 0.6, "Should find class definitions"),
            ("import", 0.6, "Should find import statements"),
            ("function", 0.5, "Should find function definitions"),
            ("validate", 0.4, "Should find validation functions"),
            ("process", 0.3, "Should find processing functions"),
        ]
        
        for query, threshold, description in search_tests:
            results = await project_manager.search(query, limit=5, threshold=threshold)
            assert len(results) > 0, f"{description}: No results for '{query}' with threshold {threshold}"
            
            # Verify result structure
            for result in results:
                assert 'similarity' in result, "Result should have similarity score"
                assert 'content' in result, "Result should have content"
                assert 'file_path' in result, "Result should have file path"
                assert result['similarity'] >= threshold, f"Similarity should be >= {threshold}"

    @pytest.mark.asyncio
    async def test_incremental_indexing(self, temp_dir: Path):
        """Test incremental indexing when files change."""
        # Initial setup
        config = Config(chunk_size=64)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-incremental")
        
        # Create initial file
        test_file = temp_dir / "evolving.py"
        test_file.write_text("""
def initial_function():
    '''Initial function.'''
    return "initial"
""")
        
        # Initial indexing
        await project_manager.index_all()
        initial_status = await project_manager.get_status()
        initial_chunks = initial_status['total_chunks']
        
        # Search for initial content
        initial_results = await project_manager.search("initial", limit=5, threshold=0.5)
        assert len(initial_results) > 0, "Should find initial content"
        
        # Modify the file
        test_file.write_text("""
def initial_function():
    '''Initial function - updated.'''
    return "initial"

def new_function():
    '''New function added.'''
    return "new"

class NewClass:
    '''New class added.'''
    
    def method(self):
        '''New method.'''
        return "method"
""")
        
        # Incremental indexing
        await project_manager.index_changes()
        updated_status = await project_manager.get_status()
        updated_chunks = updated_status['total_chunks']
        
        # Should have more chunks after adding content
        assert updated_chunks > initial_chunks, "Should have more chunks after adding content"
        
        # Should find both old and new content
        initial_results_after = await project_manager.search("initial", limit=5, threshold=0.5)
        new_results = await project_manager.search("new", limit=5, threshold=0.7)
        
        assert len(initial_results_after) > 0, "Should still find initial content"
        assert len(new_results) > 0, "Should find new content"

    @pytest.mark.asyncio
    async def test_multi_language_project(self, temp_dir: Path):
        """Test workflow with multiple programming languages."""
        # Create files in different languages
        files_content = {
            "app.py": """
import flask
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    '''Get data endpoint.'''
    return jsonify({'data': 'python_data'})

class DatabaseManager:
    '''Manage database connections.'''
    
    def __init__(self):
        self.connections = {}
    
    async def connect(self, db_name):
        '''Connect to database.'''
        return f"connected_to_{db_name}"
""",
            "server.js": """
const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

class APIServer {
    constructor(port) {
        this.port = port;
        this.server = null;
    }
    
    async start() {
        return new Promise((resolve) => {
            this.server = app.listen(this.port, () => {
                console.log(`Server running on port ${this.port}`);
                resolve();
            });
        });
    }
    
    async stop() {
        if (this.server) {
            this.server.close();
        }
    }
}

app.get('/api/status', (req, res) => {
    res.json({ status: 'javascript_ok' });
});

module.exports = { APIServer };
""",
            "utils.go": """
package main

import (
    "fmt"
    "time"
    "encoding/json"
)

type DataProcessor struct {
    Name string
    Started time.Time
}

func NewDataProcessor(name string) *DataProcessor {
    return &DataProcessor{
        Name: name,
        Started: time.Now(),
    }
}

func (dp *DataProcessor) ProcessData(data map[string]interface{}) (map[string]interface{}, error) {
    result := make(map[string]interface{})
    result["processed"] = true
    result["processor"] = dp.Name
    result["timestamp"] = dp.Started
    
    for key, value := range data {
        result[key] = value
    }
    
    return result, nil
}

func main() {
    processor := NewDataProcessor("go_processor")
    
    testData := map[string]interface{}{
        "id": 1,
        "message": "test_data",
    }
    
    result, err := processor.ProcessData(testData)
    if err != nil {
        fmt.Printf("Error: %v\\n", err)
        return
    }
    
    jsonData, _ := json.Marshal(result)
    fmt.Printf("Result: %s\\n", jsonData)
}
""",
        }
        
        # Create all files
        for filename, content in files_content.items():
            file_path = temp_dir / filename
            file_path.write_text(content)
        
        # Initialize and index
        config = Config(chunk_size=128)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-multilang")
        await project_manager.index_all()
        
        # Test cross-language searches
        cross_language_tests = [
            ("class", "Should find classes in multiple languages"),
            ("function", "Should find functions in multiple languages"),
            ("async", "Should find async patterns"),
            ("server", "Should find server-related code"),
            ("data", "Should find data processing code"),
        ]
        
        for query, description in cross_language_tests:
            results = await project_manager.search(query, limit=10, threshold=0.3)
            assert len(results) > 0, f"{description}: No results for '{query}'"
            
            # Check that we get results from multiple file types
            file_extensions = set()
            for result in results:
                path = result['file_path']
                if '.' in path:
                    ext = path.split('.')[-1]
                    file_extensions.add(ext)
            
            # For common terms, we should find results in multiple languages
            if query in ["class", "function", "data"]:
                assert len(file_extensions) >= 2, \
                    f"Should find '{query}' in multiple languages, found in: {file_extensions}"

    @pytest.mark.asyncio
    async def test_large_project_handling(self, temp_dir: Path):
        """Test handling of larger projects with many files."""
        # Create multiple files to simulate a larger project
        num_files = 20
        
        for i in range(num_files):
            file_path = temp_dir / f"module_{i:02d}.py"
            content = f"""
# Module {i} - Auto-generated for testing
import os
import sys
from typing import List, Dict, Optional

class Module{i}Handler:
    '''Handler for module {i} operations.'''
    
    def __init__(self):
        self.module_id = {i}
        self.processed_items = []
        
    async def process_items(self, items: List[Dict]) -> List[Dict]:
        '''Process items for module {i}.'''
        results = []
        for item in items:
            if self.validate_item_{i}(item):
                processed = self.transform_item_{i}(item)
                results.append(processed)
                self.processed_items.append(processed)
        return results
    
    def validate_item_{i}(self, item: Dict) -> bool:
        '''Validate item for module {i}.'''
        required_fields = ['id', 'type', 'module_{i}_data']
        return all(field in item for field in required_fields)
    
    def transform_item_{i}(self, item: Dict) -> Dict:
        '''Transform item for module {i}.'''
        return {{
            **item,
            'module_id': {i},
            'processed': True,
            'transform_version': '1.{i}.0'
        }}
    
    def get_stats_{i}(self) -> Dict:
        '''Get statistics for module {i}.'''
        return {{
            'module_id': {i},
            'total_processed': len(self.processed_items),
            'handler_type': 'Module{i}Handler'
        }}

def create_module_{i}_handler() -> Module{i}Handler:
    '''Factory function for module {i} handler.'''
    return Module{i}Handler()

async def main_module_{i}():
    '''Main function for module {i}.'''
    handler = create_module_{i}_handler()
    
    test_items = [
        {{'id': j, 'type': 'test', 'module_{i}_data': f'data_{{j}}'}}
        for j in range(3)
    ]
    
    results = await handler.process_items(test_items)
    stats = handler.get_stats_{i}()
    
    print(f"Module {i}: Processed {{len(results)}} items")
    print(f"Module {i}: Stats {{stats}}")
    
    return results

if __name__ == "__main__":
    import asyncio
    asyncio.run(main_module_{i}())
"""
            file_path.write_text(content)
        
        # Initialize and index the large project
        config = Config(chunk_size=128)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-large-project")
        
        # Measure indexing time and results
        import time
        start_time = time.time()
        await project_manager.index_all()
        end_time = time.time()
        
        indexing_time = end_time - start_time
        print(f"Indexed {num_files} files in {indexing_time:.2f} seconds")
        
        # Verify indexing results
        status = await project_manager.get_status()
        assert status['total_files'] == num_files, f"Should index {num_files} files"
        assert status['indexed_files'] == num_files, f"Should mark {num_files} files as indexed"
        assert status['total_chunks'] > num_files * 5, "Should generate substantial chunks"
        
        # Test searches on large dataset
        search_performance_tests = [
            ("async", 0.8),
            ("class", 0.8), 
            ("Handler", 0.7),
            ("process", 0.6),
            ("validate", 0.6),
            ("module", 0.5),
        ]
        
        for query, threshold in search_performance_tests:
            start_search = time.time()
            results = await project_manager.search(query, limit=20, threshold=threshold)
            end_search = time.time()
            
            search_time = end_search - start_search
            
            assert len(results) > 0, f"Should find results for '{query}'"
            assert search_time < 2.0, f"Search should be fast, took {search_time:.2f}s"
            
            # Results should be properly ranked
            similarities = [r['similarity'] for r in results]
            assert similarities == sorted(similarities, reverse=True), \
                "Results should be sorted by similarity"

    @pytest.mark.asyncio 
    async def test_project_statistics_and_status(self, temp_dir: Path):
        """Test project statistics and status reporting."""
        # Create sample files
        files = {
            "main.py": "def main(): pass\nclass App: pass",
            "utils.py": "def helper(): return True\nasync def async_helper(): pass",
            "models.py": "class User: pass\nclass Post: pass\nclass Comment: pass",
            "config.json": '{"setting": "value"}',
            "README.md": "# Project Documentation\nThis is a test project.",
        }
        
        for filename, content in files.items():
            (temp_dir / filename).write_text(content)
        
        # Initialize and index
        config = Config(chunk_size=64)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-statistics")
        await project_manager.index_all()
        
        # Get detailed status
        status = await project_manager.get_status()
        
        # Verify status structure
        required_fields = [
            'name', 'path', 'embedding_model', 'total_files', 
            'indexed_files', 'total_chunks', 'last_updated', 'created_at'
        ]
        
        for field in required_fields:
            assert field in status, f"Status should include {field}"
        
        # Verify status values
        assert status['name'] == "test-statistics"
        assert str(temp_dir) in status['path']
        assert status['total_files'] >= 3, "Should count Python files"  # .json and .md might be excluded
        assert status['indexed_files'] == status['total_files'], "All files should be indexed"
        assert status['total_chunks'] > 10, "Should generate reasonable number of chunks"
        
        # Test file listing
        files_list = await project_manager.list_files()
        assert len(files_list) >= 3, "Should list files"
        
        for file_info in files_list:
            assert 'path' in file_info
            assert 'size' in file_info
            assert 'modified' in file_info
            assert 'type' in file_info
        
        # Test file filtering
        py_files = await project_manager.list_files("py")
        assert len(py_files) >= 3, "Should find Python files"
        
        for py_file in py_files:
            assert py_file['path'].endswith('.py'), "Should only return Python files"