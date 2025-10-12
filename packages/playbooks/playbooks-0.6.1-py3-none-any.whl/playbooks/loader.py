from glob import glob
from pathlib import Path
from typing import List, Tuple

from .exceptions import ProgramLoadError
from .import_processor import ImportProcessor
from .utils.file_utils import is_compiled_playbook_file


class Loader:
    @staticmethod
    def read_program(program_paths: List[str]) -> str:
        """
        Load program content from file paths.
        """
        program_content = None
        try:
            program_content, do_not_compile = Loader._read_program(program_paths)
        except FileNotFoundError as e:
            raise ProgramLoadError(str(e)) from e
        except (OSError, IOError) as e:
            raise ProgramLoadError(str(e)) from e

        return program_content, do_not_compile

    @staticmethod
    def _read_program(paths: List[str]) -> str:
        """
        Load program content from file paths. Supports both single files and glob patterns.

        Args:
            paths: List of file paths or glob patterns (e.g., 'my_playbooks/**/*.pb')

        Returns:
            str: Combined contents of all matching program files

        Raises:
            FileNotFoundError: If no files are found or if files are empty
        """
        all_files = []

        for path in paths:
            # Simplified glob pattern check
            if "*" in str(path) or "?" in str(path) or "[" in str(path):
                # Handle glob pattern
                all_files.extend(glob(path, recursive=True))
            else:
                # Handle single file
                all_files.append(path)

        if not all_files:
            raise FileNotFoundError("No files found")

        # Deduplicate files and read content
        contents = []
        do_not_compile = False
        not_found = []
        for file in set(all_files):
            file_path = Path(file)
            if file_path.is_file() and file_path.exists():
                if is_compiled_playbook_file(file_path):
                    do_not_compile = True
                contents.append(file_path.read_text())
            else:
                not_found.append(str(file_path))

        if not_found:
            raise FileNotFoundError(f"{', '.join(not_found)} not found")

        program_contents = "\n\n".join(contents)

        if not program_contents:
            raise FileNotFoundError("Files found but content is empty")

        return program_contents, do_not_compile

    @staticmethod
    def read_program_files(program_paths: List[str]) -> List[Tuple[str, str, bool]]:
        """
        Load program files individually.

        Args:
            program_paths: List of file paths or glob patterns

        Returns:
            List of (file_path, content, is_compiled) tuples

        Raises:
            ProgramLoadError: If files cannot be read
        """
        try:
            return Loader._read_program_files(program_paths)
        except FileNotFoundError as e:
            raise ProgramLoadError(str(e)) from e
        except (OSError, IOError) as e:
            raise ProgramLoadError(str(e)) from e

    @staticmethod
    def _read_program_files(paths: List[str]) -> List[Tuple[str, str, bool]]:
        """
        Load program files individually with their metadata.
        Processes !import directives in non-compiled files.

        Args:
            paths: List of file paths or glob patterns

        Returns:
            List of (file_path, content, is_compiled) tuples

        Raises:
            FileNotFoundError: If no files are found or cannot be read
        """
        all_files = []

        for path in paths:
            # Simplified glob pattern check
            if "*" in str(path) or "?" in str(path) or "[" in str(path):
                # Handle glob pattern
                all_files.extend(glob(path, recursive=True))
            else:
                # Handle single file
                all_files.append(path)

        if not all_files:
            raise FileNotFoundError("No files found")

        # Initialize import processor
        import_processor = ImportProcessor()

        # Read files individually
        files_data = []
        not_found = []

        for file in all_files:
            file_path = Path(file)
            if file_path.is_file() and file_path.exists():
                content = file_path.read_text()
                is_compiled = is_compiled_playbook_file(file_path)

                # Process imports for non-compiled files
                if not is_compiled and "!import" in content:
                    try:
                        # Reset processor for each file to avoid cross-file state
                        import_processor.reset()
                        content = import_processor.process_imports(content, file_path)
                    except ProgramLoadError as e:
                        # Re-raise with more context
                        raise ProgramLoadError(
                            f"Error processing imports in {file_path}: {str(e)}"
                        ) from e

                files_data.append((str(file_path), content, is_compiled))
            else:
                not_found.append(str(file_path))

        if not_found:
            raise FileNotFoundError(f"{', '.join(not_found)} not found")

        if not files_data:
            raise FileNotFoundError("No valid files found")

        # Check for empty content
        if all(not content.strip() for _, content, _ in files_data):
            raise FileNotFoundError("Files found but all content is empty")

        return files_data
