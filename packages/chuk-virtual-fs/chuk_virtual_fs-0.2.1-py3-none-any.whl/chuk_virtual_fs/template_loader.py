"""
chuk_virtual_fs/template_loader.py - Async file template and preloading system
"""

from __future__ import annotations

import glob
import json
import os
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from chuk_virtual_fs.fs_manager import AsyncVirtualFileSystem


class AsyncTemplateLoader:
    """
    Template loader for preloading filesystem with files and directories

    This allows:
    - Loading files from templates or real filesystem
    - Preloading common configurations
    - Setting up sandbox environments
    - Populating filesystems with sample data
    """

    def __init__(self, fs: AsyncVirtualFileSystem) -> None:
        """
        Initialize the template loader

        Args:
            fs: The virtual filesystem instance to populate
        """
        self.fs = fs

    async def load_template(
        self,
        template_path: str,
        target_path: str = "/",
        variables: dict[str, str] | None = None,
    ) -> bool:
        """
        Load a template from file and apply it to the filesystem

        Args:
            template_path: Path to template file (YAML or JSON)
            target_path: Base path in virtual filesystem to load into
            variables: Optional variables for template substitution

        Returns:
            True if template was loaded successfully, False otherwise
        """
        try:
            # Load template file
            with open(template_path) as f:
                if template_path.endswith((".yaml", ".yml")):
                    template_data = yaml.safe_load(f)
                elif template_path.endswith(".json"):
                    template_data = json.load(f)
                else:
                    print(f"Unsupported template format: {template_path}")
                    return False

            # Apply the template
            success = await self.apply_template(template_data, target_path, variables)
            return success

        except Exception as e:
            print(f"Error loading template: {e}")
            return False

    async def apply_template(
        self,
        template_data: dict[str, Any],
        target_path: str = "/",
        variables: dict[str, str] | None = None,
    ) -> bool:
        """
        Apply a template from a dictionary structure

        Args:
            template_data: Template data as a dictionary
            target_path: Base path in virtual filesystem to load into
            variables: Optional variables for template substitution

        Returns:
            True if template was applied successfully, False otherwise
        """
        try:
            # Normalize target path
            if not target_path.endswith("/"):
                target_path = target_path + "/"

            # Make sure target directory exists
            if not await self.fs.get_node_info(target_path):
                parent_path = os.path.dirname(target_path.rstrip("/"))
                if parent_path:
                    await self._ensure_directory(parent_path)
                await self.fs.mkdir(target_path)

            # Process directories first
            directories = template_data.get("directories", [])
            if directories:
                await self._create_directories(directories, target_path, variables)

            # Process files
            files = template_data.get("files", [])
            if files:
                await self._create_files(files, target_path, variables)

            # Process symbolic links (if supported)
            links = template_data.get("links", [])
            if links and hasattr(self.fs, "create_symlink"):
                await self._create_links(links, target_path, variables)

            return True

        except Exception as e:
            print(f"Error applying template: {e}")
            return False

    async def preload_directory(
        self,
        source_dir: str,
        target_path: str = "/",
        pattern: str = "*",
        recursive: bool = True,
    ) -> int:
        """
        Preload a directory from the host filesystem

        Args:
            source_dir: Directory on the host filesystem to load files from
            target_path: Base path in virtual filesystem to load into
            pattern: File pattern to match (e.g., "*.txt", "data_*.csv")
            recursive: Whether to traverse subdirectories

        Returns:
            Number of files loaded
        """
        # Normalize source and target paths
        source_dir = os.path.abspath(source_dir)
        if not target_path.endswith("/"):
            target_path = target_path + "/"

        # Make sure target directory exists
        if not await self.fs.get_node_info(target_path):
            parent_path = os.path.dirname(target_path.rstrip("/"))
            if parent_path:
                await self._ensure_directory(parent_path)
            await self.fs.mkdir(target_path)

        # Count loaded files
        loaded_count = 0

        # Find all matching files
        if recursive:
            search_pattern = os.path.join(source_dir, "**", pattern)
            matched_files = glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = os.path.join(source_dir, pattern)
            matched_files = glob.glob(search_pattern)

        # Process each file
        for source_file in matched_files:
            if os.path.isdir(source_file):
                # Create corresponding directory in virtual filesystem
                rel_path = os.path.relpath(source_file, source_dir)
                target_dir = os.path.join(target_path, rel_path).replace("\\", "/")

                # Create directory if it doesn't exist
                if not await self.fs.get_node_info(target_dir):
                    await self._ensure_directory(target_dir)

            elif os.path.isfile(source_file):
                # Calculate relative path and create target path
                rel_path = os.path.relpath(source_file, source_dir)
                target_file = os.path.join(target_path, rel_path).replace("\\", "/")

                # Ensure parent directory exists
                parent_dir = os.path.dirname(target_file)
                if parent_dir:
                    await self._ensure_directory(parent_dir)

                # Read source file content
                try:
                    with open(source_file, errors="replace") as f:
                        content = f.read()

                    # Write to virtual filesystem
                    if await self.fs.write_file(target_file, content):
                        loaded_count += 1

                except Exception as e:
                    print(f"Error loading file {source_file}: {e}")

        return loaded_count

    async def quick_load(
        self, content_dict: dict[str, str], base_path: str = "/"
    ) -> int:
        """
        Quickly load multiple files specified as a dictionary

        Args:
            content_dict: Dictionary with paths as keys and content as values
            base_path: Base path to prepend to relative paths

        Returns:
            Number of files loaded
        """
        loaded_count = 0

        for path, content in content_dict.items():
            # Normalize path
            if not path.startswith("/"):
                path = os.path.join(base_path, path).replace("\\", "/")

            # Ensure parent directory exists
            parent_dir = os.path.dirname(path)
            if parent_dir:
                await self._ensure_directory(parent_dir)

            # Write file
            if await self.fs.write_file(path, content):
                loaded_count += 1

        return loaded_count

    async def load_from_template_directory(self, template_dir: str) -> dict[str, int]:
        """
        Load all templates from a directory

        Args:
            template_dir: Directory containing template files (.yaml, .yml, .json)

        Returns:
            Dictionary with template names and success counts
        """
        results = {}

        # Find all template files
        template_patterns = ["*.yaml", "*.yml", "*.json"]
        template_files = []

        for pattern in template_patterns:
            search_pattern = os.path.join(template_dir, pattern)
            template_files.extend(glob.glob(search_pattern))

        # Process each template
        for template_file in template_files:
            template_name = os.path.basename(template_file)
            try:
                success = await self.load_template(template_file)
                results[template_name] = 1 if success else 0
            except Exception as e:
                print(f"Error processing template {template_name}: {e}")
                results[template_name] = 0

        return results

    def _process_variables(self, text: str, variables: dict[str, str]) -> str:
        """
        Process variable substitutions in text

        Args:
            text: Text to process
            variables: Dictionary of variable name/value pairs

        Returns:
            Processed text with variables substituted
        """
        if not variables or not isinstance(text, str):
            return text

        result = text
        for var_name, var_value in variables.items():
            placeholder = f"${{{var_name}}}"
            result = result.replace(placeholder, str(var_value))

        return result

    async def _ensure_directory(self, path: str) -> bool:
        """
        Ensure a directory exists, creating parent directories as needed

        Args:
            path: Directory path to create

        Returns:
            True if successful, False otherwise
        """
        # Split path into components
        components = path.strip("/").split("/")
        current_path = "/"

        for component in components:
            if not component:
                continue

            current_path = os.path.join(current_path, component).replace("\\", "/")

            # Check if directory exists
            info = await self.fs.get_node_info(current_path)
            if not info:
                # Create directory
                if not await self.fs.mkdir(current_path):
                    return False
            elif not info.is_dir:
                # Path exists but is not a directory
                return False

        return True

    async def _create_directories(
        self,
        directories: list[Any],
        base_path: str,
        variables: dict[str, str] | None,
    ) -> None:
        """
        Create directories from template

        Args:
            directories: List of directory definitions
            base_path: Base path to create directories under
            variables: Variables for template substitution
        """
        for dir_def in directories:
            if isinstance(dir_def, str):
                # Simple directory path
                dir_path = dir_def
            elif isinstance(dir_def, dict) and "path" in dir_def:
                # Directory with path and attributes
                dir_path = dir_def["path"]
            else:
                print(f"Invalid directory definition: {dir_def}")
                continue

            # Process variables in path
            if variables:
                dir_path = self._process_variables(dir_path, variables)

            # Create full path
            full_path = os.path.join(base_path, dir_path.lstrip("/")).replace("\\", "/")

            # Create directory
            await self._ensure_directory(full_path)

    async def _create_files(
        self,
        files: list[Any],
        base_path: str,
        variables: dict[str, str] | None,
    ) -> None:
        """
        Create files from template

        Args:
            files: List of file definitions
            base_path: Base path to create files under
            variables: Variables for template substitution
        """
        for file_def in files:
            if not isinstance(file_def, dict):
                print(f"Invalid file definition: {file_def}")
                continue

            # Get file path and content
            file_path = file_def.get("path")
            content = file_def.get("content", "")
            content_file = file_def.get("content_from")

            if not file_path:
                print("Missing 'path' in file definition")
                continue

            # Process variables in path and content
            if variables:
                file_path = self._process_variables(file_path, variables)
                if isinstance(content, str):
                    content = self._process_variables(content, variables)

            # If content_from is specified, load content from file
            if content_file:
                try:
                    with open(content_file, errors="replace") as f:
                        content = f.read()
                except Exception as e:
                    print(f"Error loading content from {content_file}: {e}")
                    continue

            # Create full path
            full_path = os.path.join(base_path, file_path.lstrip("/")).replace(
                "\\", "/"
            )

            # Ensure parent directory exists
            parent_dir = os.path.dirname(full_path)
            if parent_dir:
                await self._ensure_directory(parent_dir)

            # Write file
            await self.fs.write_file(full_path, content)

    async def _create_links(
        self,
        links: list[Any],
        base_path: str,
        variables: dict[str, str] | None,
    ) -> None:
        """
        Create symbolic links from template

        Args:
            links: List of link definitions
            base_path: Base path to create links under
            variables: Variables for template substitution
        """
        # Check if symlinks are supported
        if not hasattr(self.fs, "create_symlink"):
            print("Symbolic links not supported by this filesystem")
            return

        for link_def in links:
            if not isinstance(link_def, dict):
                print(f"Invalid link definition: {link_def}")
                continue

            # Get link path and target
            link_path = link_def.get("path")
            target = link_def.get("target")

            if not link_path or not target:
                print("Missing 'path' or 'target' in link definition")
                continue

            # Process variables in path and target
            if variables:
                link_path = self._process_variables(link_path, variables)
                target = self._process_variables(target, variables)

            # Create full path
            full_path = os.path.join(base_path, link_path.lstrip("/")).replace(
                "\\", "/"
            )

            # Ensure parent directory exists
            parent_dir = os.path.dirname(full_path)
            if parent_dir:
                await self._ensure_directory(parent_dir)

            # Create symlink
            await self.fs.create_symlink(full_path, target)


# Backwards compatibility alias
TemplateLoader = AsyncTemplateLoader
