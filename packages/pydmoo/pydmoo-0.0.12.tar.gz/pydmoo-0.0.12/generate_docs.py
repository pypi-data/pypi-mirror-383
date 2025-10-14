#!/usr/bin/env python3

"""
Documentation Generation Script.

This script is used to automatically generate API documentation for the pydmoo library.
It scans the source code directory and generates corresponding Markdown files for MkDocs build.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List


class DocGenerator:
    """Documentation generator class."""

    def __init__(self, source_dir: str = "pydmoo", docs_dir: str = "docs"):
        """
        Initialize the documentation generator.

        Parameters
        ----------
        source_dir : str
            Python source code directory
        docs_dir : str
            Documentation output directory
        """
        self.source_dir = Path(source_dir)
        self.docs_dir = Path(docs_dir)
        self.api_dir = self.docs_dir / "api-auto"

        # Create necessary directories
        self.api_dir.mkdir(parents=True, exist_ok=True)

    def discover_modules(self) -> List[Path]:
        """
        Discover all Python modules.

        Returns
        -------
        List[Path]
            List of found Python module paths
        """
        modules = []

        for py_file in self.source_dir.rglob("*.py"):
            # Skip __pycache__ directories and test files
            if "__pycache__" in str(py_file) or "test" in str(py_file).lower():
                continue

            # Skip empty files and __init__.py files (handled separately)
            if py_file.name == "__init__.py":
                continue

            modules.append(py_file)

        return modules

    def get_module_info(self, module_path: Path) -> Dict[str, Any]:
        """
        Get module information.

        Parameters
        ----------
        module_path : Path
            Module file path

        Returns
        -------
        Dict[str, Any]
            Module information dictionary
        """
        # Calculate relative import path
        relative_path = module_path.relative_to(self.source_dir)
        module_name = str(relative_path).replace("/", ".").replace("\\", ".").replace(".py", "")

        return {
            "path": module_path,
            "name": module_name,
            "import_path": f"pydmoo.{module_name}",
            "doc_path": self.api_dir / f"{module_name}.md"
        }

    def generate_module_doc(self, module_info: Dict[str, Any]) -> str:
        """
        Generate documentation content for a single module.

        Parameters
        ----------
        module_info : Dict[str, Any]
            Module information

        Returns
        -------
        str
            Markdown formatted documentation content
        """
        module_name = module_info["name"]
        import_path = module_info["import_path"]

        content = [
            f"# {module_name}",
            "",
            f"::: {import_path}",
            "    options:",
            "      show_root_heading: false",
            "      show_submodules: true",
            "      heading_level: 2",
            "      show_source: true",
            "      show_category_heading: true",
            ""
        ]

        return "\n".join(content)

    def generate_package_doc(self) -> str:
        """
        Generate documentation for the main package.

        Returns
        -------
        str
            Main package documentation content
        """
        content = [
            "# pydmoo API Reference",
            "",
            "pydmoo is a dynamic multi-objective optimization library providing various optimization algorithms and tools.",
            "",
            "## Module Overview",
            "",
            "::: pydmoo",
            "    options:",
            "      show_root_heading: false",
            "      show_submodules: true",
            "      heading_level: 3",
            "      show_source: false",
            ""
        ]

        return "\n".join(content)

    def generate_api_index(self) -> str:
        """
        Generate API index page.

        Returns
        -------
        str
            Index page content
        """
        modules = self.discover_modules()
        module_infos = [self.get_module_info(module) for module in modules]

        content = [
            "# API Reference",
            "",
            "This is the complete API reference documentation for the pydmoo library.",
            "",
            "## Module List",
            ""
        ]

        # Group modules by directory
        modules_by_dir = {}
        for info in module_infos:
            dir_path = str(Path(info["name"]).parent)
            if dir_path == ".":
                dir_path = "Root Modules"
            if dir_path not in modules_by_dir:
                modules_by_dir[dir_path] = []
            modules_by_dir[dir_path].append(info)

        # Generate directory structure
        for dir_name in sorted(modules_by_dir.keys()):
            content.append(f"### {dir_name}")
            content.append("")

            for info in sorted(modules_by_dir[dir_name], key=lambda x: x["name"]):
                module_name = info["name"]
                doc_file = f"api-auto/{module_name}.md"
                content.append(f"- [{module_name}]({doc_file})")

            content.append("")

        return "\n".join(content)

    def write_file(self, filepath: Path, content: str) -> None:
        """
        Write content to file.

        Parameters
        ----------
        filepath : Path
            File path
        content : str
            File content
        """
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✓ Generated documentation: {filepath}")

    def generate_all(self) -> None:
        """Generate all documentation."""
        print("Starting API documentation generation...")

        # Generate documentation for individual modules
        modules = self.discover_modules()
        print(f"Found {len(modules)} modules")

        for module_path in modules:
            module_info = self.get_module_info(module_path)
            doc_content = self.generate_module_doc(module_info)
            self.write_file(module_info["doc_path"], doc_content)

        # Generate API index
        api_index_content = self.generate_api_index()
        self.write_file(self.docs_dir / "api-auto.md", api_index_content)

        # Generate main package documentation
        package_content = self.generate_package_doc()
        self.write_file(self.api_dir / "pydmoo.md", package_content)

        print("Documentation generation completed!")


def main():
    try:
        # Check if source code directory exists
        if not os.path.exists("pydmoo"):
            print("Error: pydmoo directory not found")
            print("Please ensure you are running this script from the project root directory")
            sys.exit(1)

        # Generate documentation
        generator = DocGenerator()
        generator.generate_all()

        # Verify generated files
        api_files = list(Path("docs/api").glob("*.md"))
        print(f"Generated {len(api_files)} API documentation files")

    except Exception as e:
        print(f"Error generating documentation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
