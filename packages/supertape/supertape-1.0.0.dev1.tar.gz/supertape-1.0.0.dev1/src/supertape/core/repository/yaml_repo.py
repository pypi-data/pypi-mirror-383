from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import yaml

from supertape.core.file.api import DataBlock, TapeFile
from supertape.core.repository.api import RepositoryInfo, TapeFileRepository, TapeFileRepositoryObserver


class YamlRepository(TapeFileRepository):
    """YAML-based tape file repository implementation.

    Stores tape files as individual YAML files in a directory structure.
    Each tape file is serialized with its metadata and data blocks.
    """

    def __init__(self, repository_dir: str | None, observers: list[TapeFileRepositoryObserver]) -> None:
        """Initialize YAML repository.

        Args:
            repository_dir: Directory to store YAML files, or None for default (~/.supertape/tapes)
            observers: List of observers to notify on repository changes
        """
        self.repository_dir: Path = (
            Path(repository_dir) if repository_dir else Path.home() / ".supertape" / "tapes"
        )
        self.observers: list[TapeFileRepositoryObserver] = observers

        # Create repository directory if it doesn't exist
        self.repository_dir.mkdir(parents=True, exist_ok=True)

    def __str__(self) -> str:
        """String representation of the repository."""
        return f"YamlRepository at {self.repository_dir}"

    def _tape_to_dict(self, tape: TapeFile) -> dict[str, Any]:
        """Convert TapeFile to dictionary for YAML serialization.

        Args:
            tape: TapeFile to convert

        Returns:
            Dictionary representation suitable for YAML serialization
        """
        return {
            "metadata": {
                "fname": tape.fname,
                "ftype": tape.ftype,
                "fdatatype": tape.fdatatype,
                "fgap": tape.fgap,
                "fstartaddress": tape.fstartaddress,
                "floadaddress": tape.floadaddress,
            },
            "blocks": [
                {
                    "type": block.type,
                    "body": base64.b64encode(bytes(block.body)).decode("ascii"),
                    "checksum": block.checksum,
                }
                for block in tape.blocks
            ],
        }

    def _dict_to_tape(self, data: dict[str, Any]) -> TapeFile:
        """Convert dictionary from YAML to TapeFile.

        Args:
            data: Dictionary loaded from YAML

        Returns:
            TapeFile reconstructed from the dictionary data
        """
        blocks: list[DataBlock] = []
        for block_data in data["blocks"]:
            body: list[int] = list(base64.b64decode(block_data["body"].encode("ascii")))
            block: DataBlock = DataBlock(block_data["type"], body)
            blocks.append(block)

        return TapeFile(blocks)

    def _get_file_path(self, tape: TapeFile) -> Path:
        """Get the file path for a tape file.

        Args:
            tape: TapeFile to get path for

        Returns:
            Path where the tape file should be stored
        """
        safe_name: str = "".join(c for c in tape.fname if c.isalnum() or c in (" ", "-", "_")).strip()
        if not safe_name:
            safe_name = f"tape_{id(tape)}"
        return self.repository_dir / f"{safe_name}.yaml"

    def add_tape_file(self, file: TapeFile) -> None:
        """Add a tape file to the repository.

        Args:
            file: TapeFile to add to the repository
        """
        file_path: Path = self._get_file_path(file)

        # Handle duplicate names by appending a number
        counter: int = 1
        original_path: Path = file_path
        while file_path.exists():
            stem: str = original_path.stem
            file_path = original_path.parent / f"{stem}_{counter}.yaml"
            counter += 1

        data: dict[str, Any] = self._tape_to_dict(file)
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)

        for observer in self.observers:
            observer.file_added(file)

    def remove_tape_file(self, file: TapeFile) -> None:
        """Remove a tape file from the repository.

        Args:
            file: TapeFile to remove from the repository
        """
        # Find and remove the file
        for yaml_file in self.repository_dir.glob("*.yaml"):
            try:
                with open(yaml_file, encoding="utf-8") as f:
                    data: dict[str, Any] | None = yaml.safe_load(f)

                if data is not None:
                    existing_tape: TapeFile = self._dict_to_tape(data)
                    if existing_tape == file:
                        yaml_file.unlink()
                        for observer in self.observers:
                            observer.file_removed(file)
                        return
            except (yaml.YAMLError, KeyError, ValueError, TypeError):
                # Skip corrupted files
                continue

    def get_tape_files(self) -> list[TapeFile]:
        """Get all tape files from the repository.

        Returns:
            List of all TapeFile objects in the repository
        """
        tapes: list[TapeFile] = []

        for yaml_file in self.repository_dir.glob("*.yaml"):
            try:
                with open(yaml_file, encoding="utf-8") as f:
                    data: dict[str, Any] | None = yaml.safe_load(f)

                if data is not None:
                    tape: TapeFile = self._dict_to_tape(data)
                    tapes.append(tape)
            except (yaml.YAMLError, KeyError, ValueError, TypeError):
                # Skip corrupted files
                continue

        return tapes

    def add_observer(self, observer: TapeFileRepositoryObserver) -> None:
        """Add an observer."""
        self.observers.append(observer)

    def remove_observer(self, observer: TapeFileRepositoryObserver) -> None:
        """Remove an observer."""
        self.observers.remove(observer)

    def get_repository_info(self) -> RepositoryInfo:
        """Get information about the repository.

        Returns:
            RepositoryInfo object containing:
            - file_count: Number of files in the repository
            - path: Repository storage path (absolute)
            - type: Repository type ("yaml")
            - storage_size: Total size of stored YAML files in bytes
        """
        yaml_files = list(self.repository_dir.glob("*.yaml"))
        file_count = len(yaml_files)

        # Calculate total storage size
        storage_size = sum(yaml_file.stat().st_size for yaml_file in yaml_files)

        return RepositoryInfo(
            file_count=file_count,
            path=str(self.repository_dir.absolute()),
            type="yaml",
            storage_size=storage_size,
        )
