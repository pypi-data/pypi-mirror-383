"""Project manager that coordinates all components."""

import asyncio
import gc
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import git
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Try to import psutil for memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from .config import Config
from ..db.chromadb_manager import ChromaDBManager
from ..vectorizer.engine import VectorizationEngine

logger = logging.getLogger(__name__)


class ProjectManager:
    """Manages a vectorized project."""
    
    def __init__(self, project_path: Path, config: Config):
        self.project_path = Path(project_path).resolve()
        self.config = config
        self.project = None

        # Check if project path exists
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")

        # Create ChromaDB database manager
        chroma_path = config.get_chromadb_path(project_path)
        self.db = ChromaDBManager(chroma_path)

        self.vectorizer = VectorizationEngine(
            embedding_model=config.embedding_model,
            embedding_provider=config.embedding_provider,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            openai_api_key=config.openai_api_key
        )

        # Git integration
        self.git_repo = None
        try:
            self.git_repo = git.Repo(self.project_path)
        except git.exc.InvalidGitRepositoryError:
            logger.warning(f"No git repository found at {project_path}")

        # File watching
        self.observer = None
        self.file_handler = None

        # Memory management tracking
        self._files_processed_since_gc = 0

        # Progress tracking callback
        self._progress_callback = None

    def set_progress_callback(self, callback: callable):
        """
        Set a progress callback function.

        The callback will be called with (current, total, description) parameters.

        Example:
            def progress_cb(current, total, description):
                print(f"Progress: {current}/{total} - {description}")

            project_manager.set_progress_callback(progress_cb)
        """
        self._progress_callback = callback

    def _report_progress(self, current: int, total: int, description: str = ""):
        """Report progress through callback if set."""
        if self._progress_callback:
            self._progress_callback(current, total, description)

    async def initialize(self, project_name: str) -> None:
        """Initialize a new project."""
        # Initialize database
        await self.db.initialize()
        
        # Initialize vectorizer
        await self.vectorizer.initialize()
        
        existing_project = await self.db.get_project_by_path(str(self.project_path))
        if existing_project:
            self.project = existing_project
            logger.info(f"Found existing project: {existing_project.name}")
        else:
            self.project = await self.db.create_project(
                name=project_name,
                path=str(self.project_path),
                embedding_model=self.config.embedding_model,
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
            logger.info(f"Created new project: {project_name}")
        
        # Save configuration
        self.config.save_to_project(self.project_path)
        
        # Scan project files initially
        await self._scan_project_files()
    
    async def load(self) -> None:
        """Load an existing project."""
        await self.db.initialize()
        await self.vectorizer.initialize()
        
        # Load project from database
        self.project = await self.db.get_project_by_path(str(self.project_path))
        if not self.project:
            raise ValueError(f"No project found at {self.project_path}")
        
        logger.info(f"Loaded project: {self.project.name}")
    
    async def _scan_project_files(self) -> None:
        """
        Scan project directory and update file records.

        Only updates files that have actually changed (by content hash or modification time).
        """
        # Only log if no progress callback
        if not self._progress_callback:
            logger.info("Scanning project files...")

        file_count = 0
        updated_count = 0

        for file_path in self._get_project_files():
            try:
                # Calculate file hash
                content_hash = self.vectorizer.calculate_file_hash(file_path)
                if not content_hash:
                    continue

                # Get file info
                stat = file_path.stat()
                relative_path = file_path.relative_to(self.project_path)

                # Check if file exists in database
                existing_file = await self.db.get_file_by_path(self.project.id, str(relative_path))

                # Only update if file is new or actually changed
                if not existing_file:
                    # New file - add it
                    await self.db.upsert_file(
                        project_id=self.project.id,
                        file_path=str(file_path),
                        relative_path=str(relative_path),
                        file_type=file_path.suffix.lower(),
                        size_bytes=stat.st_size,
                        content_hash=content_hash,
                        last_modified=datetime.fromtimestamp(stat.st_mtime)
                    )
                    updated_count += 1
                    logger.debug(f"Added new file: {relative_path}")
                elif existing_file.content_hash != content_hash:
                    # File content changed - update it
                    await self.db.upsert_file(
                        project_id=self.project.id,
                        file_path=str(file_path),
                        relative_path=str(relative_path),
                        file_type=file_path.suffix.lower(),
                        size_bytes=stat.st_size,
                        content_hash=content_hash,
                        last_modified=datetime.fromtimestamp(stat.st_mtime)
                    )
                    updated_count += 1
                    logger.debug(f"File content changed: {relative_path}")
                # else: File unchanged - skip update to preserve timestamps

                file_count += 1

            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                continue

        # Only log if no progress callback
        if not self._progress_callback:
            logger.info(f"Scanned {file_count} files ({updated_count} new/modified)")
    
    def _get_project_files(self) -> List[Path]:
        """Get all project files matching filter criteria."""
        files = []
        
        for root, dirs, filenames in os.walk(self.project_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not any(
                self.config._match_pattern(os.path.join(root, d), pattern)
                for pattern in self.config.excluded_patterns
            )]
            
            for filename in filenames:
                file_path = Path(root) / filename
                
                # Check if file should be included
                if self.config.should_include_file(file_path):
                    files.append(file_path)
        
        return files
    
    async def index_all(self) -> None:
        """Index all files in the project."""
        if self.project is None:
            raise ValueError("Project not initialized. Call initialize() first.")

        # Only log if no progress callback (so we don't clutter progress bar)
        if not self._progress_callback:
            logger.info("Starting full indexing...")

        # Reset GC counter
        self._files_processed_since_gc = 0

        # First scan for any new files that might have been added
        await self._scan_project_files()

        files_to_index = await self.db.get_files_to_index(self.project.id)
        total_files = len(files_to_index)

        for idx, file_record in enumerate(files_to_index, 1):
            self._report_progress(idx, total_files, f"Indexing {file_record.relative_path}")
            await self._index_file(file_record)

        # Final memory check
        await self._check_memory_usage()

        # Only log if no progress callback
        if not self._progress_callback:
            logger.info(f"Indexed {total_files} files")
    
    async def index_changes(self) -> None:
        """
        Index only changed files.

        Now uses smart incremental indexing by default for better performance.
        """
        # Only log if no progress callback
        if not self._progress_callback:
            logger.info("Indexing changes (using smart incremental mode)...")

        # Use smart incremental indexing by default
        stats = await self.smart_incremental_index()

        total_changes = stats['new'] + stats['modified'] + stats['deleted']
        # Only log if no progress callback
        if not self._progress_callback:
            logger.info(f"Indexed {total_changes} total changes (new: {stats['new']}, modified: {stats['modified']}, deleted: {stats['deleted']})")
    
    async def _index_file(self, file_record) -> None:
        """Index a single file."""
        try:
            file_path = Path(file_record.path)

            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return

            logger.debug(f"Indexing file: {file_record.relative_path}")

            # Process file and get chunks
            chunks = await self.vectorizer.process_file(
                file_path=file_path,
                project_id=self.project.id,
                file_id=file_record.id
            )

            if chunks:
                await self.db.save_chunks(chunks)
                await self.db.mark_file_indexed(file_record.id)
                logger.debug(f"Indexed {len(chunks)} chunks from {file_record.relative_path}")
            else:
                logger.warning(f"No chunks generated for {file_record.relative_path}")

            # Memory management
            self._trigger_gc()
            await self._check_memory_usage()

        except Exception as e:
            logger.error(f"Error indexing file {file_record.relative_path}: {e}")
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.1
    ) -> List[Dict[str, Any]]:
        if self.project is None:
            raise ValueError("Project not initialized. Call initialize() first.")

        # Validate and normalize limit
        if limit <= 0:
            limit = 1  # Minimum limit of 1 for ChromaDB compatibility

        # Normalize threshold to valid range [0, 1]
        threshold = max(0.0, min(1.0, threshold))

        # Special handling for single-word queries
        query_words = query.strip().split()
        is_single_word = len(query_words) == 1

        # Adjust threshold for single-word queries to ensure better results
        effective_threshold = threshold
        if is_single_word:
            # For single words, we want to catch exact matches even with lower semantic similarity
            effective_threshold = min(threshold, 0.3)  # Lower threshold for single words

        query_embedding = await self.vectorizer.generate_query_embedding(query)
        if query_embedding is None:
            return []

        results = await self.db.search_chunks(
            project_id=self.project.id,
            query_embedding=query_embedding,
            limit=limit * 2 if is_single_word else limit,  # Get more results for single words to ensure good matches
            threshold=effective_threshold,
            query_text=query
        )
        
        # For single-word queries, re-rank results to prioritize exact matches
        if is_single_word and results:
            word = query_words[0].lower()
            
            def priority_score(result):
                content = result['content'].lower()
                similarity = result['similarity']
                
                # Exact word match gets highest priority
                import re
                if re.search(r'\b' + re.escape(word) + r'\b', content):
                    return (3, similarity)  # Category 3: exact word match
                elif word in content:
                    return (2, similarity)  # Category 2: partial match
                else:
                    return (1, similarity)  # Category 1: semantic similarity only
            
            results.sort(key=priority_score, reverse=True)
            results = results[:limit]  # Trim back to requested limit
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                'file_path': result['file_path'],
                'content': result['content'],
                'similarity': result['similarity'],
                'line_number': result.get('start_line', 1),
                'start_line': result.get('start_line'),
                'end_line': result.get('end_line'),
                'language': result.get('language'),
                'content_type': result.get('content_type')
            })
        
        return formatted_results
    
    async def get_file_content(self, relative_path: str) -> Optional[str]:
        """Get the content of a specific file."""
        try:
            file_path = self.project_path / relative_path
            
            if not file_path.exists() or not file_path.is_file():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error reading file {relative_path}: {e}")
            return None
    
    async def list_files(self, file_type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all files in the project."""
        files = self._get_project_files()
        
        result = []
        for file_path in files:
            relative_path = file_path.relative_to(self.project_path)
            
            # Apply file type filter
            if file_type_filter:
                file_ext = file_path.suffix.lower()
                if file_type_filter not in str(relative_path).lower() and file_type_filter not in file_ext:
                    continue
            
            try:
                stat = file_path.stat()
                result.append({
                    'path': str(relative_path),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'type': file_path.suffix.lower()
                })
            except Exception as e:
                logger.error(f"Error getting file info for {relative_path}: {e}")
                continue
        
        return result
    
    async def get_status(self) -> Dict[str, Any]:
        """Get project status information."""
        stats = await self.db.get_project_stats(self.project.id)
        
        return {
            'name': self.project.name,
            'path': str(self.project_path),
            'embedding_model': self.project.embedding_model,
            'total_files': stats['total_files'],
            'indexed_files': stats['indexed_files'],
            'total_chunks': stats['total_chunks'],
            'last_updated': stats['last_updated'] or datetime.now(),
            'created_at': self.project.created_at,
            'git_branch': self._get_current_git_branch()
        }
    
    def _get_current_git_branch(self) -> Optional[str]:
        """Get current git branch."""
        if self.git_repo:
            try:
                return self.git_repo.active_branch.name
            except Exception:
                return None
        return None
    
    async def sync_changes(self) -> None:
        """Sync changes from git."""
        if not self.git_repo:
            logger.warning("No git repository found. Running regular change detection.")
            await self.index_changes()
            return

        try:
            # Get changes from git
            changed_files = self._get_git_changes()

            if changed_files:
                logger.info(f"Found {len(changed_files)} changed files from git")

                # Update file records for changed files
                await self._scan_project_files()

                # Index changes
                await self.index_changes()
            else:
                logger.info("No changes found")

        except Exception as e:
            logger.error(f"Error syncing git changes: {e}")
            await self.index_changes()

    async def smart_incremental_index(self) -> Dict[str, int]:
        """
        Smart incremental indexing with priority queue.

        Priority order:
        1. New files (never indexed)
        2. Modified files (changed since last index)
        3. Deleted files (remove from index)

        Returns:
            Dict with counts of new, modified, and deleted files
        """
        # Only log if no progress callback (so we don't clutter progress bar)
        if not self._progress_callback:
            logger.info("Starting smart incremental indexing...")

        # Scan for file system changes
        await self._scan_project_files()

        files_to_index = await self.db.get_files_to_index(self.project.id)
        all_files = await self.db.get_all_files(self.project.id)

        # Categorize files
        new_files = []
        modified_files = []

        for file in files_to_index:
            if not file.indexed_at or file.indexed_at == '':
                new_files.append(file)
            elif file.last_modified and file.indexed_at:
                # Parse dates for comparison
                try:
                    last_mod = datetime.fromisoformat(file.last_modified)
                    indexed = datetime.fromisoformat(file.indexed_at)
                    if last_mod > indexed:
                        modified_files.append(file)
                except (ValueError, AttributeError):
                    # If date parsing fails, treat as modified
                    modified_files.append(file)

        # Find deleted files
        file_paths = {f.relative_path for f in all_files}
        existing_paths = set()
        for f in all_files:
            file_full_path = self.project_path / f.relative_path
            if file_full_path.exists():
                existing_paths.add(f.relative_path)

        deleted_paths = file_paths - existing_paths

        # Log categorization only if no progress callback
        if not self._progress_callback:
            logger.info(f"[cyan]New files:[/cyan] {len(new_files)}")
            logger.info(f"[yellow]Modified files:[/yellow] {len(modified_files)}")
            logger.info(f"[red]Deleted files:[/red] {len(deleted_paths)}")

        # Calculate total work
        total_work = len(new_files) + len(modified_files) + len(deleted_paths)
        current_progress = 0

        # 1. Index new files first (highest priority)
        for file in new_files:
            current_progress += 1
            self._report_progress(current_progress, total_work, f"[New] {file.relative_path}")
            logger.debug(f"Indexing new file: {file.relative_path}")
            await self._index_file(file)

        # 2. Reindex modified files
        for file in modified_files:
            current_progress += 1
            self._report_progress(current_progress, total_work, f"[Modified] {file.relative_path}")
            logger.debug(f"Reindexing modified file: {file.relative_path}")
            await self._reindex_file_partial(file)

        # 3. Remove deleted files
        for relative_path in deleted_paths:
            current_progress += 1
            self._report_progress(current_progress, total_work, f"[Deleted] {relative_path}")
            logger.debug(f"Removing deleted file: {relative_path}")
            await self._remove_file_from_index(relative_path)

        return {
            'new': len(new_files),
            'modified': len(modified_files),
            'deleted': len(deleted_paths)
        }

    async def index_git_changes(self, since: str = "HEAD~1") -> int:
        """
        Index only files changed in recent git commits.

        Args:
            since: Git reference to compare against (e.g., 'HEAD~1', 'main', commit hash)

        Returns:
            Number of files indexed

        Examples:
            # Index changes in last commit
            await manager.index_git_changes('HEAD~1')

            # Index all changes since main branch
            await manager.index_git_changes('main')

            # Index changes since specific commit
            await manager.index_git_changes('abc123')
        """
        if not self.git_repo:
            logger.warning("Not a git repository, falling back to full indexing")
            await self.index_changes()
            return 0

        try:
            # Get changed files from git
            diff = self.git_repo.git.diff(since, '--name-only')
            changed_files = [f.strip() for f in diff.split('\n') if f.strip()]

            # Only log if no progress callback
            if not self._progress_callback:
                logger.info(f"Found {len(changed_files)} changed files since {since}")

            # Index only changed files
            indexed = 0
            total_files = len(changed_files)
            for idx, file_path in enumerate(changed_files, 1):
                full_path = self.project_path / file_path

                if full_path.exists() and self.config.should_include_file(full_path):
                    self._report_progress(idx, total_files, f"Indexing {file_path}")
                    await self._index_file_by_path(full_path)
                    indexed += 1

            # Only log if no progress callback
            if not self._progress_callback:
                logger.info(f"Indexed {indexed} files")
            return indexed

        except Exception as e:
            logger.error(f"Error reading git diff: {e}")
            logger.warning("Falling back to standard incremental indexing")
            await self.index_changes()
            return 0

    async def _index_file_by_path(self, file_path: Path) -> None:
        """Index a specific file by path."""
        # Resolve paths to handle symlinks (e.g., /var vs /private/var on macOS)
        file_path = file_path.resolve()
        project_path = self.project_path.resolve()
        relative_path = file_path.relative_to(project_path)

        # Check if file exists in database
        file_record = await self.db.get_file_by_path(self.project.id, str(relative_path))

        if file_record:
            # Reindex existing file (with partial reindexing)
            logger.debug(f"Reindexing existing file: {relative_path}")
            await self._reindex_file_partial(file_record)
        else:
            # Add new file
            logger.debug(f"Adding new file: {relative_path}")

            # Calculate hash
            content_hash = self.vectorizer.calculate_file_hash(file_path)
            if not content_hash:
                return

            # Get file info
            stat = file_path.stat()

            # Create file record
            file_record = await self.db.upsert_file(
                project_id=self.project.id,
                file_path=str(file_path),
                relative_path=str(relative_path),
                file_type=file_path.suffix.lower(),
                size_bytes=stat.st_size,
                content_hash=content_hash,
                last_modified=datetime.fromtimestamp(stat.st_mtime)
            )

            # Index the file
            await self._index_file(file_record)

    async def _remove_file_from_index(self, relative_path: str) -> None:
        """Remove a deleted file from the index."""
        try:
            file_record = await self.db.get_file_by_path(self.project.id, relative_path)

            if file_record:
                logger.debug(f"Removing file from index: {relative_path}")
                await self.db.delete_file(file_record.id)

        except Exception as e:
            logger.error(f"Error removing file {relative_path}: {e}")

    async def _reindex_file_partial(self, file_record) -> None:
        """
        Reindex only changed portions of a file.
        Compares old and new chunks to minimize work.
        """
        try:
            file_path = self.project_path / file_record.relative_path

            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return

            logger.debug(f"Partial reindexing: {file_record.relative_path}")

            # Get existing chunks for this file
            old_chunks = await self.db.get_file_chunks(self.project.id, file_record.id)

            # Generate new chunks
            new_chunks = await self.vectorizer.process_file(
                file_path=file_path,
                project_id=self.project.id,
                file_id=file_record.id
            )

            if not new_chunks:
                logger.warning(f"No chunks generated for {file_record.relative_path}")
                return

            # Compare chunks by content hash
            old_chunk_hashes = {self._hash_chunk(c['content']): c for c in old_chunks}
            new_chunk_hashes = {self._hash_chunk(c['content']): c for c in new_chunks}

            # Find differences
            removed_hashes = old_chunk_hashes.keys() - new_chunk_hashes.keys()
            added_hashes = new_chunk_hashes.keys() - old_chunk_hashes.keys()

            # If too many changes (>50%), just reindex the whole file
            change_ratio = (len(removed_hashes) + len(added_hashes)) / max(len(old_chunk_hashes), 1)
            if change_ratio > 0.5:
                logger.debug(f"High change ratio ({change_ratio:.2f}), doing full reindex")
                await self.db.save_chunks(new_chunks)
            else:
                logger.debug(f"Chunks: {len(removed_hashes)} removed, {len(added_hashes)} added")

                # Remove old chunks
                for chunk_hash in removed_hashes:
                    old_chunk = old_chunk_hashes[chunk_hash]
                    if old_chunk.get('id'):
                        await self.db.delete_chunk(self.project.id, old_chunk['id'])

                # Add only new chunks
                chunks_to_add = [new_chunk_hashes[h] for h in added_hashes]
                if chunks_to_add:
                    await self.db.save_chunks(chunks_to_add)

            # Update file metadata
            await self.db.update_file(file_record.id, indexed_at=datetime.now())
            logger.debug(f"Partial reindex complete for {file_record.relative_path}")

        except Exception as e:
            logger.error(f"Error during partial reindexing of {file_record.relative_path}: {e}")
            # Fallback to full reindexing on error
            await self._index_file(file_record)

    def _hash_chunk(self, content: str) -> str:
        """Generate hash for chunk content."""
        import hashlib
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def _check_memory_usage(self) -> None:
        """
        Monitor memory usage during indexing.

        Warns when memory usage exceeds 80% or 90% of available RAM.
        Suggests reducing batch_size or max_workers if memory is high.
        """
        if not self.config.memory_monitoring_enabled or not PSUTIL_AVAILABLE:
            return

        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            if memory_percent > 90:
                logger.warning(
                    f"Memory usage critical: {memory_percent:.1f}% "
                    f"({memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB)"
                )
                logger.warning("Consider reducing batch_size or max_workers in config")
            elif memory_percent > 80:
                logger.warning(
                    f"Memory usage high: {memory_percent:.1f}% "
                    f"({memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB)"
                )

        except Exception as e:
            logger.debug(f"Could not check memory usage: {e}")

    def _trigger_gc(self) -> None:
        """
        Force garbage collection to reclaim memory.

        Triggered based on gc_interval configuration (default: every 100 files).
        """
        self._files_processed_since_gc += 1

        if self._files_processed_since_gc >= self.config.gc_interval:
            logger.debug(f"Triggering garbage collection after {self._files_processed_since_gc} files")
            collected = gc.collect()
            logger.debug(f"Garbage collection freed {collected} objects")
            self._files_processed_since_gc = 0

    def _get_git_changes(self) -> List[str]:
        """Get list of changed files from git."""
        try:
            # Get untracked files
            untracked = self.git_repo.untracked_files
            
            # Get modified files
            modified = [item.a_path for item in self.git_repo.index.diff(None)]
            
            # Get staged files
            staged = [item.a_path for item in self.git_repo.index.diff("HEAD")]
            
            return list(set(untracked + modified + staged))
            
        except Exception as e:
            logger.error(f"Error getting git changes: {e}")
            return []
    
    async def start_watching(self, debounce_seconds: float = 2.0) -> None:
        """
        Start watching for file changes.

        Args:
            debounce_seconds: Delay before processing changes (default: 2.0)
        """
        if self.observer:
            return

        self.file_handler = ProjectFileHandler(self, debounce_seconds=debounce_seconds)
        self.file_handler.set_event_loop(asyncio.get_event_loop())
        self.observer = Observer()
        self.observer.schedule(self.file_handler, str(self.project_path), recursive=True)
        self.observer.start()

        logger.info(f"Started watching {self.project_path} (debounce: {debounce_seconds}s)")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.stop_watching()
    
    def stop_watching(self) -> None:
        """Stop watching for file changes."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.file_handler = None
            logger.info("Stopped watching for changes")


class ProjectFileHandler(FileSystemEventHandler):
    """Handle file system events for project watching."""

    def __init__(self, project_manager: ProjectManager, debounce_seconds: float = 2.0):
        self.project_manager = project_manager
        self.pending_changes = set()
        self.last_change_time = None
        self.change_debounce_delay = debounce_seconds  # configurable
        self.loop = None  # Will be set when watching starts
    
    def set_event_loop(self, loop):
        """Set the event loop for thread-safe async operations."""
        self.loop = loop
    
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_change(event.src_path)
    
    def on_created(self, event):
        if not event.is_directory:
            self._handle_change(event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self._handle_change(event.src_path)
    
    def _handle_change(self, file_path: str):
        """Handle a file change event."""
        file_path = Path(file_path)
        
        # Check if file should be included
        if not self.project_manager.config.should_include_file(file_path):
            return
        
        self.pending_changes.add(file_path)
        
        # Use time.time() instead of asyncio.get_event_loop().time() for thread safety
        import time
        self.last_change_time = time.time()
        
        # Schedule processing after debounce delay using thread-safe method
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(
                self._process_changes_after_delay(), 
                self.loop
            )
    
    async def _process_changes_after_delay(self):
        """Process changes after debounce delay."""
        await asyncio.sleep(self.change_debounce_delay)
        
        # Check if enough time has passed since last change
        import time
        if (time.time() - self.last_change_time) >= self.change_debounce_delay:
            if self.pending_changes:
                logger.info(f"Processing {len(self.pending_changes)} changed files")
                
                # Trigger incremental indexing
                try:
                    await self.project_manager.index_changes()
                    self.pending_changes.clear()
                except Exception as e:
                    logger.error(f"Error processing file changes: {e}")