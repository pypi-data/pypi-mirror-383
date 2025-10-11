"""
Git-based file change detection for incremental indexing.

This module leverages Git's built-in change tracking to detect which files
have changed since the last indexing operation, enabling efficient incremental updates.
"""

import subprocess
import logging
from pathlib import Path
from typing import List, Set, Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class GitChangeDetector:
    """
    Detect file changes using Git.

    Leverages Git's efficient change tracking to identify:
    - Files changed between commits
    - Uncommitted changes in working directory
    - New/modified/deleted files
    """

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize Git change detector.

        Args:
            repo_path: Path to Git repository (default: current directory)
        """
        self.repo_path = repo_path or Path.cwd()
        self._verify_git_repo()

    @staticmethod
    def is_git_repository(repo_path: Path) -> bool:
        """
        Check if a directory is a Git repository.

        Args:
            repo_path: Path to check

        Returns:
            True if the path is a Git repository, False otherwise
        """
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _verify_git_repo(self) -> None:
        """Verify that the path is a Git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug(f"Git repository verified at {self.repo_path}")
        except subprocess.CalledProcessError:
            raise ValueError(f"Not a Git repository: {self.repo_path}")
        except FileNotFoundError:
            raise RuntimeError("Git is not installed or not in PATH")

    def get_current_commit(self) -> str:
        """
        Get current commit hash.

        Returns:
            Current HEAD commit hash (short form)
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            commit_hash = result.stdout.strip()
            logger.debug(f"Current commit: {commit_hash}")
            return commit_hash
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get current commit: {e}")
            return ""

    def get_changed_files_since_commit(
        self, last_commit: str, file_extensions: Optional[Set[str]] = None
    ) -> List[str]:
        """
        Get files changed since a specific commit.

        Args:
            last_commit: Commit hash to compare against
            file_extensions: Optional set of file extensions to filter (e.g., {'.py', '.js'})

        Returns:
            List of changed file paths (relative to repo root)
        """
        try:
            # Get committed changes
            result = subprocess.run(
                ["git", "diff", "--name-only", last_commit, "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            changed_files = result.stdout.strip().splitlines()

            # Filter by extension if specified
            if file_extensions:
                changed_files = [
                    f for f in changed_files if Path(f).suffix in file_extensions
                ]

            logger.info(f"Found {len(changed_files)} changed files since {last_commit}")
            return changed_files

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get changed files: {e}")
            return []

    def get_uncommitted_changes(
        self, file_extensions: Optional[Set[str]] = None
    ) -> Dict[str, str]:
        """
        Get uncommitted changes in working directory.

        Args:
            file_extensions: Optional set of file extensions to filter

        Returns:
            Dict mapping file_path to status:
            - 'modified': Modified file
            - 'added': New file
            - 'deleted': Deleted file
            - 'renamed': Renamed file
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            uncommitted = {}
            for line in result.stdout.splitlines():  # Don't strip - preserves exact format
                if len(line) < 3:
                    continue

                # Git porcelain format: "XY filename" where X and Y are status codes
                # Position 0-1: status codes, Position 2: space, Position 3+: filename
                status_code = line[:2]
                # Skip the space at position 2, start from position 3
                file_path = line[3:].strip() if len(line) > 3 else ""

                if not file_path:
                    continue

                # Handle renamed files (format: "old -> new")
                if " -> " in file_path:
                    file_path = file_path.split(" -> ")[1]

                # Filter by extension if specified
                if file_extensions and Path(file_path).suffix not in file_extensions:
                    continue

                # Map Git status codes to our status
                # Git porcelain: XY where X=index, Y=worktree
                # Examples: " M" = modified in worktree, "M " = modified in index
                # "MM" = modified in both, "A " = added to index, "??" = untracked
                index_status = status_code[0]
                worktree_status = status_code[1]

                if "M" in status_code or "A" in status_code:
                    if "A" in status_code and index_status == "A":
                        uncommitted[file_path] = "added"
                    else:
                        uncommitted[file_path] = "modified"
                elif status_code == "??":
                    uncommitted[file_path] = "added"
                elif "D" in status_code:
                    uncommitted[file_path] = "deleted"
                elif "R" in status_code:
                    uncommitted[file_path] = "renamed"

            logger.info(f"Found {len(uncommitted)} uncommitted changes")
            return uncommitted

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get uncommitted changes: {e}")
            return {}

    def get_all_changed_files(
        self, last_commit: Optional[str] = None, file_extensions: Optional[Set[str]] = None
    ) -> Dict[str, str]:
        """
        Get all changed files (committed + uncommitted).

        Args:
            last_commit: Commit hash to compare against (None = only uncommitted)
            file_extensions: Optional set of file extensions to filter

        Returns:
            Dict mapping file_path to change_reason:
            - 'committed': Changed in commits since last_commit
            - 'modified': Uncommitted modification
            - 'added': Uncommitted new file
            - 'deleted': Uncommitted deletion
            - 'renamed': Uncommitted rename
        """
        all_changed = {}

        # Get committed changes
        if last_commit:
            committed = self.get_changed_files_since_commit(last_commit, file_extensions)
            for file_path in committed:
                all_changed[file_path] = "committed"

        # Get uncommitted changes
        uncommitted = self.get_uncommitted_changes(file_extensions)
        for file_path, status in uncommitted.items():
            # Uncommitted changes override committed status
            all_changed[file_path] = status

        logger.info(f"Total changed files: {len(all_changed)}")
        return all_changed

    def get_tracked_files(self, file_extensions: Optional[Set[str]] = None) -> List[str]:
        """
        Get all files tracked by Git.

        Args:
            file_extensions: Optional set of file extensions to filter

        Returns:
            List of tracked file paths
        """
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            tracked_files = result.stdout.strip().splitlines()

            # Filter by extension if specified
            if file_extensions:
                tracked_files = [
                    f for f in tracked_files if Path(f).suffix in file_extensions
                ]

            logger.debug(f"Found {len(tracked_files)} tracked files")
            return tracked_files

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get tracked files: {e}")
            return []

    def is_file_tracked(self, file_path: str) -> bool:
        """
        Check if a file is tracked by Git.

        Args:
            file_path: Path to check (relative to repo root)

        Returns:
            True if file is tracked, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "ls-files", "--error-unmatch", file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_file_last_modified_commit(self, file_path: str) -> Optional[str]:
        """
        Get the commit hash where a file was last modified.

        Args:
            file_path: Path to file (relative to repo root)

        Returns:
            Commit hash or None if not found
        """
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H", "--", file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            commit_hash = result.stdout.strip()
            return commit_hash if commit_hash else None
        except subprocess.CalledProcessError:
            return None

    def get_repository_info(self) -> Dict[str, str]:
        """
        Get repository information.

        Returns:
            Dict with repository metadata
        """
        info = {}

        try:
            # Current commit
            info["current_commit"] = self.get_current_commit()

            # Current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            info["current_branch"] = result.stdout.strip()

            # Remote URL
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            info["remote_url"] = result.stdout.strip() if result.returncode == 0 else ""

            # Repository root
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            info["repo_root"] = result.stdout.strip()

            logger.debug(f"Repository info: {info}")
            return info

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get repository info: {e}")
            return info


class IndexingMetadata:
    """
    Helper class to store/retrieve indexing metadata in collection metadata.

    Stores:
    - last_indexed_commit: Git commit hash when last indexed
    - last_indexed_timestamp: ISO timestamp of last indexing
    """

    @staticmethod
    def create_metadata(commit_hash: str) -> Dict[str, str]:
        """
        Create indexing metadata.

        Args:
            commit_hash: Current Git commit hash

        Returns:
            Metadata dict
        """
        return {
            "last_indexed_commit": commit_hash,
            "last_indexed_timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def get_last_indexed_commit(collection_metadata: Dict) -> Optional[str]:
        """
        Get last indexed commit from collection metadata.

        Args:
            collection_metadata: ChromaDB collection metadata

        Returns:
            Last indexed commit hash or None
        """
        return collection_metadata.get("last_indexed_commit")

    @staticmethod
    def should_do_incremental_update(
        collection_metadata: Dict, current_commit: str
    ) -> bool:
        """
        Determine if incremental update is possible.

        Args:
            collection_metadata: ChromaDB collection metadata
            current_commit: Current Git commit hash

        Returns:
            True if incremental update is possible, False if full re-index needed
        """
        last_commit = IndexingMetadata.get_last_indexed_commit(collection_metadata)

        if not last_commit:
            logger.info("No last indexed commit found - full indexing required")
            return False

        if last_commit == current_commit:
            logger.info("Already at current commit - checking uncommitted changes only")
            return True

        logger.info(f"Incremental update possible: {last_commit} -> {current_commit}")
        return True

