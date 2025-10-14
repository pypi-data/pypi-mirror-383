"""Code parser for extracting structured elements from source files."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import tree_sitter_python as tspython
    import tree_sitter_javascript as tsjavascript
    import tree_sitter_typescript as tstypescript
    import tree_sitter_go as tsgo
    import tree_sitter_rust as tsrust
    import tree_sitter_java as tsjava
    from tree_sitter import Language, Parser, Node
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

logger = logging.getLogger(__name__)


class CodeParser:
    """Parser for extracting structured code elements."""
    
    def __init__(self):
        self.parsers = {}
        self.languages = {}
        
        if TREE_SITTER_AVAILABLE:
            self._initialize_parsers()
        else:
            logger.warning("Tree-sitter not available. Falling back to simple parsing.")
    
    def _initialize_parsers(self):
        """Initialize Tree-sitter parsers for different languages."""
        try:
            # Initialize languages
            language_configs = {
                'python': tspython,
                'javascript': tsjavascript,
                'typescript': tstypescript,
                'tsx': tstypescript,  # TSX uses the same module as TypeScript
                'go': tsgo,
                'rust': tsrust,
                'java': tsjava,
            }
            
            for lang_name, lang_module in language_configs.items():
                try:
                    # Resolve the correct language initializer per module
                    if hasattr(lang_module, 'language'):
                        # Most language packages expose a generic `language()`
                        lang_ptr = lang_module.language()
                    elif lang_name == 'typescript' and hasattr(lang_module, 'language_typescript'):
                        lang_ptr = lang_module.language_typescript()
                    elif lang_name == 'tsx' and hasattr(lang_module, 'language_tsx'):
                        lang_ptr = lang_module.language_tsx()
                    else:
                        # Special case: tree_sitter_typescript publishes language_typescript/language_tsx
                        if lang_module is tstypescript:
                            if lang_name == 'typescript' and hasattr(lang_module, 'language_typescript'):
                                lang_ptr = lang_module.language_typescript()
                            elif lang_name == 'tsx' and hasattr(lang_module, 'language_tsx'):
                                lang_ptr = lang_module.language_tsx()
                            else:
                                raise AttributeError(f"No suitable language initializer found for {lang_name}")
                        else:
                            raise AttributeError(f"No suitable language initializer found for {lang_name}")

                    language = Language(lang_ptr)
                    parser = Parser(language)
                    
                    self.languages[lang_name] = language
                    self.parsers[lang_name] = parser
                    
                    logger.debug(f"Initialized {lang_name} parser")
                except Exception as e:
                    logger.warning(f"Could not initialize {lang_name} parser: {e}")
        
        except Exception as e:
            logger.error(f"Error initializing parsers: {e}")
    
    async def parse_file(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Parse a file and extract structured elements."""
        language = self._detect_language(file_path)
        
        if TREE_SITTER_AVAILABLE and language in self.parsers:
            return await self._parse_with_tree_sitter(content, language)
        else:
            return await self._parse_simple(content, language)
    
    async def _parse_with_tree_sitter(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Parse content using Tree-sitter."""
        try:
            parser = self.parsers[language]
            
            # Parse in executor to avoid blocking
            loop = asyncio.get_event_loop()
            tree = await loop.run_in_executor(
                None, parser.parse, content.encode('utf-8')
            )
            
            elements = []
            
            if language == 'python':
                elements.extend(await self._extract_python_elements(tree.root_node, content))
            elif language in ['javascript', 'typescript', 'tsx']:
                elements.extend(await self._extract_js_elements(tree.root_node, content))
            elif language == 'go':
                elements.extend(await self._extract_go_elements(tree.root_node, content))
            elif language == 'rust':
                elements.extend(await self._extract_rust_elements(tree.root_node, content))
            elif language == 'java':
                elements.extend(await self._extract_java_elements(tree.root_node, content))
            
            return elements
            
        except Exception as e:
            logger.error(f"Error parsing with tree-sitter: {e}")
            return await self._parse_simple(content, language)
    
    async def _extract_python_elements(self, root_node: Node, content: str) -> List[Dict[str, Any]]:
        """Extract Python code elements."""
        elements = []
        lines = content.split('\n')
        
        def extract_node_content(node: Node) -> str:
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            return '\n'.join(lines[start_line:end_line + 1])
        
        def traverse(node: Node):
            if node.type in ['function_definition', 'async_function_definition']:
                # Extract function
                func_content = extract_node_content(node)
                elements.append({
                    'type': 'function',
                    'name': self._get_node_name(node),
                    'content': func_content,
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1,
                    'docstring': self._extract_python_docstring(node, lines)
                })
            
            elif node.type == 'class_definition':
                # Extract class
                class_content = extract_node_content(node)
                elements.append({
                    'type': 'class',
                    'name': self._get_node_name(node),
                    'content': class_content,
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1,
                    'docstring': self._extract_python_docstring(node, lines)
                })
            
            # Continue traversing children
            for child in node.children:
                traverse(child)
        
        traverse(root_node)
        return elements
    
    async def _extract_js_elements(self, root_node: Node, content: str) -> List[Dict[str, Any]]:
        """Extract JavaScript/TypeScript code elements."""
        elements = []
        lines = content.split('\n')
        
        def extract_node_content(node: Node) -> str:
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            return '\n'.join(lines[start_line:end_line + 1])
        
        def traverse(node: Node):
            if node.type in ['function_declaration', 'function_expression', 'arrow_function', 'method_definition']:
                # Extract function
                func_content = extract_node_content(node)
                elements.append({
                    'type': 'function',
                    'name': self._get_node_name(node) or 'anonymous',
                    'content': func_content,
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1
                })
            
            elif node.type == 'class_declaration':
                # Extract class
                class_content = extract_node_content(node)
                elements.append({
                    'type': 'class',
                    'name': self._get_node_name(node),
                    'content': class_content,
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1
                })
            
            # Continue traversing children
            for child in node.children:
                traverse(child)
        
        traverse(root_node)
        return elements
    
    async def _extract_go_elements(self, root_node: Node, content: str) -> List[Dict[str, Any]]:
        """Extract Go code elements."""
        elements = []
        lines = content.split('\n')
        
        def extract_node_content(node: Node) -> str:
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            return '\n'.join(lines[start_line:end_line + 1])
        
        def traverse(node: Node):
            if node.type == 'function_declaration':
                func_content = extract_node_content(node)
                elements.append({
                    'type': 'function',
                    'name': self._get_node_name(node),
                    'content': func_content,
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1
                })
            
            elif node.type == 'type_declaration':
                type_content = extract_node_content(node)
                elements.append({
                    'type': 'type',
                    'name': self._get_node_name(node),
                    'content': type_content,
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1
                })
            
            for child in node.children:
                traverse(child)
        
        traverse(root_node)
        return elements
    
    async def _extract_rust_elements(self, root_node: Node, content: str) -> List[Dict[str, Any]]:
        """Extract Rust code elements."""
        elements = []
        lines = content.split('\n')
        
        def extract_node_content(node: Node) -> str:
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            return '\n'.join(lines[start_line:end_line + 1])
        
        def traverse(node: Node):
            if node.type == 'function_item':
                func_content = extract_node_content(node)
                elements.append({
                    'type': 'function',
                    'name': self._get_node_name(node),
                    'content': func_content,
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1
                })
            
            elif node.type in ['struct_item', 'enum_item', 'impl_item']:
                item_content = extract_node_content(node)
                elements.append({
                    'type': node.type.replace('_item', ''),
                    'name': self._get_node_name(node),
                    'content': item_content,
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1
                })
            
            for child in node.children:
                traverse(child)
        
        traverse(root_node)
        return elements
    
    async def _extract_java_elements(self, root_node: Node, content: str) -> List[Dict[str, Any]]:
        """Extract Java code elements."""
        elements = []
        lines = content.split('\n')
        
        def extract_node_content(node: Node) -> str:
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            return '\n'.join(lines[start_line:end_line + 1])
        
        def traverse(node: Node):
            if node.type == 'method_declaration':
                method_content = extract_node_content(node)
                elements.append({
                    'type': 'method',
                    'name': self._get_node_name(node),
                    'content': method_content,
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1
                })
            
            elif node.type == 'class_declaration':
                class_content = extract_node_content(node)
                elements.append({
                    'type': 'class',
                    'name': self._get_node_name(node),
                    'content': class_content,
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1
                })
            
            for child in node.children:
                traverse(child)
        
        traverse(root_node)
        return elements
    
    def _get_node_name(self, node: Node) -> Optional[str]:
        """Get the name of a node (function, class, etc.)."""
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode('utf-8')
        return None
    
    def _extract_python_docstring(self, node: Node, lines: List[str]) -> Optional[str]:
        """Extract docstring from Python function/class."""
        # Look for string literal as first statement in body
        for child in node.children:
            if child.type == 'block':
                for stmt in child.children:
                    if stmt.type == 'expression_statement':
                        for expr in stmt.children:
                            if expr.type == 'string':
                                start_line = expr.start_point[0]
                                end_line = expr.end_point[0]
                                return '\n'.join(lines[start_line:end_line + 1]).strip('"""').strip("'''").strip()
        return None
    
    async def _parse_simple(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Simple regex-based parsing fallback."""
        import re
        
        elements = []
        lines = content.split('\n')
        
        if language == 'python':
            # Simple Python function/class detection
            patterns = [
                (r'^(class\s+\w+.*?):', 'class'),
                (r'^(def\s+\w+.*?):', 'function'),
                (r'^(async\s+def\s+\w+.*?):', 'function'),
            ]
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                for pattern, element_type in patterns:
                    match = re.match(pattern, line_stripped)
                    if match:
                        # Find the end of the block (simplified)
                        end_line = self._find_python_block_end(lines, i)
                        block_content = '\n'.join(lines[i:end_line + 1])
                        
                        elements.append({
                            'type': element_type,
                            'name': self._extract_name_from_def(match.group(1)),
                            'content': block_content,
                            'start_line': i + 1,
                            'end_line': end_line + 1
                        })
        
        elif language in ['javascript', 'typescript']:
            # Simple JS function detection
            patterns = [
                (r'function\s+(\w+)', 'function'),
                (r'class\s+(\w+)', 'class'),
                (r'const\s+(\w+)\s*=\s*(?:async\s+)?\(', 'function'),
                (r'(\w+)\s*:\s*(?:async\s+)?function', 'function'),
            ]
            
            for i, line in enumerate(lines):
                for pattern, element_type in patterns:
                    match = re.search(pattern, line)
                    if match:
                        # Find matching braces (simplified)
                        end_line = self._find_js_block_end(lines, i)
                        block_content = '\n'.join(lines[i:end_line + 1])
                        
                        elements.append({
                            'type': element_type,
                            'name': match.group(1),
                            'content': block_content,
                            'start_line': i + 1,
                            'end_line': end_line + 1
                        })
        
        return elements
    
    def _find_python_block_end(self, lines: List[str], start: int) -> int:
        """Find the end of a Python code block."""
        indent_level = len(lines[start]) - len(lines[start].lstrip())
        
        for i in range(start + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                continue
            
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and line.strip():
                return i - 1
        
        return len(lines) - 1
    
    def _find_js_block_end(self, lines: List[str], start: int) -> int:
        """Find the end of a JavaScript code block."""
        brace_count = 0
        found_opening = False
        
        for i in range(start, len(lines)):
            line = lines[i]
            for char in line:
                if char == '{':
                    brace_count += 1
                    found_opening = True
                elif char == '}':
                    brace_count -= 1
                    if found_opening and brace_count == 0:
                        return i
        
        return len(lines) - 1
    
    def _extract_name_from_def(self, def_line: str) -> str:
        """Extract name from Python function/class definition."""
        import re
        match = re.search(r'(?:class|def)\s+(\w+)', def_line)
        return match.group(1) if match else 'unknown'
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect language from file extension."""
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'tsx',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
        }
        return ext_to_lang.get(file_path.suffix.lower(), 'text')
