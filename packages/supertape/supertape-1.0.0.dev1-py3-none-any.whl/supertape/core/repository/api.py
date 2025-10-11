from __future__ import annotations

from dataclasses import dataclass

from supertape.core.file.api import TapeFile


@dataclass(frozen=True)
class RepositoryInfo:
    """Repository information record."""

    file_count: int
    path: str
    type: str
    storage_size: int


class TapeFileRepositoryObserver:
    """Observer interface for tape file repository events."""

    def file_added(self, file: TapeFile) -> None:
        """Called when a file is added to the repository."""
        pass

    def file_removed(self, file: TapeFile) -> None:
        """Called when a file is removed from the repository."""
        pass


class TapeFileRepository:
    """Abstract base class for tape file repositories."""

    def add_tape_file(self, file: TapeFile) -> None:
        """Add a tape file to the repository."""
        raise NotImplementedError

    def remove_tape_file(self, file: TapeFile) -> None:
        """Remove a tape file from the repository."""
        raise NotImplementedError

    def get_tape_files(self) -> list[TapeFile]:
        """Get all tape files from the repository."""
        raise NotImplementedError

    def add_observer(self, observer: TapeFileRepositoryObserver) -> None:
        """Add an observer to watch repository events."""
        raise NotImplementedError

    def remove_observer(self, observer: TapeFileRepositoryObserver) -> None:
        """Remove an observer from watching repository events."""
        raise NotImplementedError

    def get_repository_info(self) -> RepositoryInfo:
        """Get information about the repository.

        Returns:
            RepositoryInfo dictionary containing:
            - file_count: Number of files in the repository
            - path: Repository storage path
            - type: Repository type (e.g., "yaml")
            - storage_size: Total size of stored files in bytes
        """
        raise NotImplementedError
