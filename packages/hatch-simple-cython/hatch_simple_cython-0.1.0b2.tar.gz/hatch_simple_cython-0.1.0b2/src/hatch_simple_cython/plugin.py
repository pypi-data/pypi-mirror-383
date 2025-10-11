# SPDX-License-Identifier: MIT
"""Main plugin implementation for SimpleCythonBuildHook."""

import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class SimpleCythonBuildHook(BuildHookInterface):
    """A simplified Cython build hook for Hatch.

    This hook automatically discovers and compiles Cython files (.pyx)
    with minimal configuration required.
    """

    PLUGIN_NAME = "simple-cython"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._options = None

    @property
    def options(self) -> dict[str, Any]:
        """Parse and cache configuration options."""
        if self._options is None:
            # Configuration is directly in self.config, not under "options"
            config = self.config
            self._options = {
                "directives": config.get("directives", {"language_level": "3"}),
                "compile_args": config.get("compile_args", ["-O2"]),
                "link_args": config.get("link_args", []),
                "include_dirs": config.get("include_dirs", []),
                "libraries": config.get("libraries", []),
                "library_dirs": config.get("library_dirs", []),
                "define_macros": config.get("define_macros", []),
                "compile_py": config.get("compile_py", False),
                "include_numpy": config.get("include_numpy", False),
                "cythonize_kwargs": config.get("cythonize_kwargs", {}),
            }

            # Add numpy includes if requested
            if self._options["include_numpy"]:
                try:
                    import numpy

                    numpy_include = numpy.get_include()
                    if numpy_include not in self._options["include_dirs"]:
                        self._options["include_dirs"].append(numpy_include)
                except ImportError:
                    self.app.display_warning(
                        "include_numpy is True but numpy is not installed"
                    )

        return self._options

    @property
    def is_src_layout(self) -> bool:
        """Check if project uses src/ layout."""
        return os.path.exists(os.path.join(self.root, "src"))

    @property
    def package_dir(self) -> str:
        """Get the package directory path."""
        # Check if user specified package directory in config
        if "package_dir" in self.config:
            return self.config["package_dir"]
        
        # Try to auto-detect from filesystem
        derived_name = self.metadata.name.replace("-", "_")
        
        # Check if derived_name directory exists
        if os.path.exists(os.path.join(self.root, derived_name)):
            pkg_name = derived_name
        elif os.path.exists(os.path.join(self.root, "src", derived_name)):
            pkg_name = derived_name
        else:
            # List directories and find Python packages (with __init__.py)
            candidates = []
            for d in os.listdir(self.root):
                full_path = os.path.join(self.root, d)
                if (os.path.isdir(full_path) and 
                    not d.startswith('.') and 
                    d not in ['build', 'dist', '__pycache__', 'tests', 'docs'] and
                    os.path.exists(os.path.join(full_path, '__init__.py'))):
                    candidates.append(d)
            
            if candidates:
                pkg_name = candidates[0]
            else:
                pkg_name = derived_name
        
        # Construct full path
        if self.is_src_layout:
            return f"./src/{pkg_name}"
        return f"./{pkg_name}"

    def find_cython_files(self) -> list[str]:
        """Find all Cython source files to compile."""
        patterns = ["**/*.pyx"]

        # Include .py files if configured
        if self.options["compile_py"]:
            patterns.append("**/*.py")

        files = []
        base_dir = Path(self.root) / self.package_dir.lstrip("./")

        for pattern in patterns:
            found = base_dir.glob(pattern)
            for f in found:
                # Skip __pycache__ and other unwanted files
                if "__pycache__" in str(f):
                    continue
                # Convert to relative path from root
                rel_path = f.relative_to(self.root)
                files.append(str(rel_path).replace("\\", "/"))

        return files

    def group_files_by_module(self, files: list[str]) -> list[dict[str, Any]]:
        """Group files into extension modules.

        Each .pyx file becomes a separate extension module.
        """
        extensions = []

        for file_path in files:
            # Convert file path to module name
            # e.g., src/pkg/module.pyx -> pkg.module
            path = Path(file_path)

            # Remove extension
            parts = list(path.with_suffix("").parts)

            # Remove 'src' if present
            if parts and parts[0] == "src":
                parts = parts[1:]

            # Create module name
            module_name = ".".join(parts)

            extensions.append(
                {
                    "name": module_name,
                    "sources": [file_path],
                }
            )

        return extensions

    def generate_setup_script(
        self, extensions: list[dict[str, Any]], output_path: str
    ) -> None:
        """Generate a temporary setup.py script for building extensions."""
        opts = self.options

        # Format options for the setup script
        include_dirs_repr = repr(opts["include_dirs"])
        libraries_repr = repr(opts["libraries"])
        library_dirs_repr = repr(opts["library_dirs"])
        compile_args_repr = repr(opts["compile_args"])
        link_args_repr = repr(opts["link_args"])
        define_macros_repr = repr(opts["define_macros"])
        directives_repr = repr(opts["directives"])
        cythonize_kwargs_repr = ", ".join(
            f"{k}={v!r}" for k, v in opts["cythonize_kwargs"].items()
        )

        extensions_repr = repr(extensions)

        setup_code = f"""
from setuptools import Extension, setup
from Cython.Build import cythonize

EXTENSIONS = {extensions_repr}

ext_modules = [
    Extension(
        ext["name"],
        ext["sources"],
        include_dirs={include_dirs_repr},
        libraries={libraries_repr},
        library_dirs={library_dirs_repr},
        extra_compile_args={compile_args_repr},
        extra_link_args={link_args_repr},
        define_macros={define_macros_repr},
    )
    for ext in EXTENSIONS
]

cythonized = cythonize(
    ext_modules,
    compiler_directives={directives_repr},
    {cythonize_kwargs_repr}
)

if __name__ == "__main__":
    setup(ext_modules=cythonized)
"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(setup_code)

    def build_extensions(self) -> dict[str, str]:
        """Build Cython extensions and return inclusion map."""
        files = self.find_cython_files()

        if not files:
            self.app.display_info("No Cython files found to compile")
            return {}

        self.app.display_info(f"Found {len(files)} Cython file(s) to compile")
        for f in files:
            self.app.display_debug(f"  - {f}")

        extensions = self.group_files_by_module(files)

        with TemporaryDirectory() as temp_dir:
            setup_file = os.path.join(temp_dir, "setup.py")
            build_temp = os.path.join(temp_dir, "build_temp")
            build_lib = os.path.join(temp_dir, "build_lib")

            os.makedirs(build_temp, exist_ok=True)
            os.makedirs(build_lib, exist_ok=True)

            self.generate_setup_script(extensions, setup_file)

            # Log the setup script for debugging
            self.app.display_debug("Generated setup.py:")
            with open(setup_file, encoding="utf-8") as f:
                for line in f:
                    self.app.display_debug(f"  {line.rstrip()}")

            # Build extensions
            cmd = [
                sys.executable,
                setup_file,
                "build_ext",
                "--inplace",
                "--build-temp",
                build_temp,
                "--build-lib",
                build_lib,
            ]

            self.app.display_info("Building Cython extensions...")

            result = subprocess.run(
                cmd,
                cwd=self.root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            if result.returncode != 0:
                self.app.display_error("Cython compilation failed!")
                if result.stdout:
                    self.app.display_error(result.stdout)
                if result.stderr:
                    self.app.display_error(result.stderr)
                raise RuntimeError("Cython compilation failed")

            self.app.display_debug("Build output:")
            if result.stdout:
                for line in result.stdout.splitlines():
                    self.app.display_debug(f"  {line}")

        # Build inclusion map for compiled extensions
        inclusion_map = {}

        # Find all compiled .so/.pyd files
        for root, dirs, filenames in os.walk(self.root):
            # Skip build directories
            if "build" in root or "__pycache__" in root:
                continue

            for filename in filenames:
                if filename.endswith((".so", ".pyd", ".dll")):
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, self.root)
                    inclusion_map[rel_path] = rel_path

        self.app.display_info(f"Built {len(inclusion_map)} extension(s)")
        for path in inclusion_map:
            self.app.display_debug(f"  - {path}")

        return inclusion_map

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Hook called before the build process.

        This is where we compile Cython extensions and register them
        with the build system.
        """
        self.app.display_mini_header("simple-cython")

        # Only build for wheel targets
        if self.target_name != "wheel":
            self.app.display_info(
                f"Skipping Cython compilation for {self.target_name} target"
            )
            return

        try:
            inclusion_map = self.build_extensions()

            if inclusion_map:
                # Register compiled extensions with build system
                build_data["force_include"].update(inclusion_map)

                # Mark as not pure Python
                build_data["pure_python"] = False

                # Enable platform-specific tags
                build_data["infer_tag"] = True

                self.app.display_success("Cython extensions built successfully")

        except Exception as e:
            self.app.display_error(f"Error during Cython compilation: {e}")
            raise

    def clean(self, versions: list[str]) -> None:
        """Clean up build artifacts."""
        self.app.display_info("Cleaning Cython build artifacts...")

        # Find and remove compiled extensions and C files
        for root, dirs, files in os.walk(self.root):
            if "__pycache__" in root or "build" in root:
                continue

            for filename in files:
                # Remove compiled extensions
                if filename.endswith((".so", ".pyd", ".dll")):
                    filepath = os.path.join(root, filename)
                    self.app.display_debug(f"Removing {filepath}")
                    try:
                        os.remove(filepath)
                    except OSError as e:
                        self.app.display_warning(f"Failed to remove {filepath}: {e}")

                # Remove generated C files
                elif filename.endswith(".c") or filename.endswith(".cpp"):
                    # Check if corresponding .pyx file exists
                    base = filename.rsplit(".", 1)[0]
                    pyx_file = os.path.join(root, f"{base}.pyx")
                    if os.path.exists(pyx_file):
                        filepath = os.path.join(root, filename)
                        self.app.display_debug(f"Removing {filepath}")
                        try:
                            os.remove(filepath)
                        except OSError as e:
                            self.app.display_warning(
                                f"Failed to remove {filepath}: {e}"
                            )
