"""
Static external class analyzer for param-lsp.

This module provides static analysis of external Parameterized classes without
runtime module loading. It uses AST parsing to extract parameter information
from source files directly.
"""

from __future__ import annotations

import importlib.metadata
import logging
import site
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import parso

from param_lsp.cache import external_library_cache
from param_lsp.constants import ALLOWED_EXTERNAL_LIBRARIES
from param_lsp.models import ParameterInfo, ParameterizedInfo

from . import parso_utils
from .ast_navigator import ImportHandler, ParameterDetector
from .parameter_extractor import extract_parameter_info_from_assignment

if TYPE_CHECKING:
    from parso.tree import NodeOrLeaf

logger = logging.getLogger(__name__)

_STDLIB_MODULES = tuple(f"{c}." for c in ("__future__", *sys.stdlib_module_names))


class ExternalClassInspector:
    """Static analyzer for external Parameterized classes.

    Analyzes external libraries using pure AST parsing without runtime imports.
    Discovers source files and extracts parameter information statically.
    """

    def __init__(self):
        self.library_source_paths: dict[str, list[Path]] = {}
        self.parsed_classes: dict[str, ParameterizedInfo | None] = {}
        self.analyzed_files: dict[Path, dict[str, Any]] = {}
        self.file_source_cache: dict[
            Path, list[str]
        ] = {}  # Store source lines for parameter extraction
        # Cache all class AST nodes for inheritance resolution
        self.class_ast_cache: dict[str, tuple[NodeOrLeaf, dict[str, str]]] = {}
        # Multi-file analysis queue
        self.analysis_queue: list[tuple[Path, str]] = []  # (file_path, reason)
        self.currently_analyzing: set[Path] = set()  # Prevent circular analysis
        self.current_file_context: Path | None = None  # Track current file for import resolution
        # Track which libraries have been pre-populated in this session
        self.populated_libraries: set[str] = set()

    def _get_library_dependencies(self, library_name: str) -> list[str]:
        """Get dependencies of a library that are also in ALLOWED_EXTERNAL_LIBRARIES.

        Args:
            library_name: Name of the library to check

        Returns:
            List of dependency library names that are allowed external libraries
        """
        dependencies = []
        try:
            metadata = importlib.metadata.metadata(library_name)
            requires = metadata.get_all("Requires-Dist") or []

            for req in requires:
                # Parse requirement string (e.g., "panel>=1.0" -> "panel")
                dep_name = req.split(";")[0].split(">=")[0].split("==")[0].split("<")[0].strip()

                # Only include if it's in our allowed list
                if dep_name in ALLOWED_EXTERNAL_LIBRARIES and dep_name != library_name:
                    dependencies.append(dep_name)
                    logger.debug(f"Found dependency: {library_name} -> {dep_name}")

        except Exception as e:
            logger.debug(f"Could not get dependencies for {library_name}: {e}")

        return dependencies

    def populate_library_cache(self, library_name: str) -> int:
        """Pre-populate cache with all Parameterized classes from a library.

        Uses iterative inheritance resolution to find all classes that transitively
        inherit from param.Parameterized, including through intermediate base classes.

        Also populates dependencies first to ensure transitive inheritance through
        dependency classes is captured correctly.

        Args:
            library_name: Name of the library (e.g., "panel", "holoviews")

        Returns:
            Number of classes cached
        """
        if library_name not in ALLOWED_EXTERNAL_LIBRARIES:
            logger.debug(f"Library {library_name} not in allowed list")
            return 0

        # Check if we've already populated this library in this session
        if library_name in self.populated_libraries:
            logger.debug(f"Already populated {library_name} in this session")
            return 0

        # Mark as populated to avoid re-running
        self.populated_libraries.add(library_name)

        # Check if cache already has content for this library
        if external_library_cache.has_library_cache(library_name):
            logger.debug(f"Cache already exists for {library_name}")
            return 0

        # Populate dependencies first to ensure we can resolve inheritance
        # from classes in dependent libraries
        dependencies = self._get_library_dependencies(library_name)
        for dep in dependencies:
            if dep not in self.populated_libraries:
                logger.info(f"Pre-populating dependency {dep} for {library_name}")
                self.populate_library_cache(dep)

        logger.info(f"Pre-populating cache for {library_name} using iterative resolution")

        # Discover all source files for the library
        source_paths = self._discover_library_sources(library_name)
        if not source_paths:
            logger.debug(f"No source files found for {library_name}")
            return 0

        # Phase 1: Build inheritance map
        logger.debug("Phase 1: Building inheritance map")
        inheritance_map: dict[str, list[str]] = {}  # full_class_path -> [base_class_paths]
        class_ast_nodes: dict[
            str, tuple[NodeOrLeaf, dict[str, str], Path]
        ] = {}  # full_class_path -> (ast_node, imports, source_file)

        for source_path in source_paths:
            try:
                source_code = source_path.read_text(encoding="utf-8")
                tree = parso.parse(source_code)

                # Extract imports for this file
                file_imports: dict[str, str] = {}
                import_handler = ImportHandler(file_imports)
                for node in parso_utils.walk_tree(tree):
                    import_handler.handle_import(node)

                # Cache source lines for later parameter extraction
                self.file_source_cache[source_path] = source_code.split("\n")

                # Find all class definitions
                for node in parso_utils.walk_tree(tree):
                    if node.type == "classdef":
                        class_name = parso_utils.get_class_name(node)
                        if not class_name:
                            continue

                        # Construct full class path
                        full_class_path = self._get_full_class_path(
                            source_path, class_name, library_name
                        )
                        if not full_class_path:
                            continue

                        # Get base classes as full paths
                        bases = self._resolve_base_class_paths(node, file_imports, library_name)

                        # Store in inheritance map
                        inheritance_map[full_class_path] = bases
                        class_ast_nodes[full_class_path] = (node, file_imports, source_path)

            except Exception as e:
                logger.debug(f"Error processing {source_path}: {e}")
                continue

        logger.debug(f"Found {len(inheritance_map)} classes in inheritance map")

        # Phase 2: Iterative Parameterized detection
        logger.debug("Phase 2: Iterative Parameterized detection")
        parameterized_classes: set[str] = set()

        # Round 1: Find direct Parameterized subclasses
        for class_path, bases in inheritance_map.items():
            if any(self._is_parameterized_base(base) for base in bases):
                parameterized_classes.add(class_path)

        logger.debug(
            f"Round 1: Found {len(parameterized_classes)} direct Parameterized subclasses"
        )

        # Round 2+: Propagate iteratively
        round_num = 2
        changed = True
        while changed:
            changed = False
            for class_path, bases in inheritance_map.items():
                if class_path not in parameterized_classes:
                    # Check if any base class is already marked as Parameterized
                    for base in bases:
                        if self._base_matches_parameterized_class(base, parameterized_classes):
                            parameterized_classes.add(class_path)
                            changed = True
                            break

            if changed:
                logger.debug(
                    f"Round {round_num}: Total {len(parameterized_classes)} Parameterized classes"
                )
                round_num += 1

        logger.debug(f"Final: Found {len(parameterized_classes)} total Parameterized classes")

        # Phase 3: Extract parameters for Parameterized classes
        logger.debug("Phase 3: Extracting parameters")
        count = 0
        for class_path in parameterized_classes:
            try:
                class_node, file_imports, source_path = class_ast_nodes[class_path]
                class_info = self._convert_ast_to_class_info(
                    class_node, file_imports, class_path, source_path
                )
                if class_info:
                    external_library_cache.set(library_name, class_path, class_info)
                    count += 1
            except Exception as e:
                logger.debug(f"Failed to cache {class_path}: {e}")

        logger.info(f"Pre-populated {count} classes for {library_name}")
        # Clean up AST caches after population
        self._cleanup_ast_caches()
        return count

    def analyze_external_class(self, full_class_path: str) -> ParameterizedInfo | None:
        """Analyze an external class using static analysis.

        Args:
            full_class_path: Full path like "panel.widgets.IntSlider"

        Returns:
            ParameterizedInfo if successful, None otherwise
        """
        # Quick check for core param types that are not Parameterized classes
        if full_class_path.startswith("param."):
            # These are parameter types, not Parameterized classes - cache and return None
            self.parsed_classes[full_class_path] = None
            return None

        if full_class_path in self.parsed_classes:
            return self.parsed_classes[full_class_path]

        # Check if this library is allowed
        root_module = full_class_path.split(".")[0]
        if root_module not in ALLOWED_EXTERNAL_LIBRARIES:
            logger.debug(f"Library {root_module} not in allowed list")
            self.parsed_classes[full_class_path] = None
            return None

        # Try to populate cache if not already done
        self.populate_library_cache(root_module)

        try:
            # First, try to get from cache (which may contain pre-populated data)
            class_info = external_library_cache.get(root_module, full_class_path)
            if class_info:
                logger.debug(f"Found cached metadata for {full_class_path}")
                self.parsed_classes[full_class_path] = class_info
                return class_info

            # Fallback to dynamic AST analysis
            logger.debug(f"No cached metadata found for {full_class_path}, trying AST analysis")
            class_info = self._analyze_class_from_source(full_class_path)
            self.parsed_classes[full_class_path] = class_info

            # Store successful analysis in global cache for persistence
            if class_info:
                try:
                    external_library_cache.set(root_module, full_class_path, class_info)
                    logger.debug(f"Stored {full_class_path} in cache")
                except Exception as e:
                    logger.debug(f"Failed to store {full_class_path} in cache: {e}")

            return class_info
        except Exception as e:
            logger.debug(f"Failed to analyze {full_class_path}: {e}")
            self.parsed_classes[full_class_path] = None
            return None

    def _analyze_class_from_source(self, full_class_path: str) -> ParameterizedInfo | None:
        """Analyze a class by finding and parsing its source file.

        Args:
            full_class_path: Full class path like "panel.widgets.IntSlider"

        Returns:
            ParameterizedInfo if found and analyzed successfully
        """
        # Parse the class path
        parts = full_class_path.split(".")
        root_module = parts[0]
        class_name = parts[-1]

        # Find source files for this library
        source_paths = self._discover_library_sources(root_module)
        if not source_paths:
            logger.debug(f"No source files found for {root_module}")
            return None

        # Search for the class in source files using queue-based analysis
        for source_path in source_paths:
            try:
                # Queue the initial file for analysis
                self._queue_file_for_analysis(source_path, f"searching for {class_name}")

                # Process the analysis queue
                self._process_analysis_queue()

                # Check if we found the class
                class_info = self._find_class_definition(class_name)
                if class_info:
                    class_definition, class_imports = class_info
                    # Verify this is actually a Parameterized class
                    if self._inherits_from_parameterized(class_definition, class_imports):
                        # Convert AST node to ParameterizedInfo
                        result = self._convert_ast_to_class_info(
                            class_definition, class_imports, full_class_path, source_path
                        )
                        # Clean up AST caches after successful conversion
                        self._cleanup_ast_caches()
                        return result

            except Exception as e:
                logger.debug(f"Error analyzing {source_path}: {e}")
                continue

        logger.debug(f"Class {full_class_path} not found in source files")
        # Clean up AST caches when class not found
        self._cleanup_ast_caches()
        return None

    def _get_full_class_path(
        self, source_path: Path, class_name: str, library_name: str
    ) -> str | None:
        """Construct full class path from source file path and class name.

        Args:
            source_path: Path to the source file
            class_name: Name of the class
            library_name: Root library name (e.g., "panel")

        Returns:
            Full class path like "panel.widgets.IntSlider" or None if unable to construct
        """
        try:
            # Find the library root directory
            for site_dir in [*site.getsitepackages(), site.getusersitepackages()]:
                if site_dir and Path(site_dir).exists():
                    library_path = Path(site_dir) / library_name
                    if library_path.exists() and source_path.is_relative_to(library_path):
                        # Get relative path from library root
                        relative_path = source_path.relative_to(library_path)
                        # Convert path to module notation
                        parts = list(relative_path.parts[:-1])  # Exclude filename
                        if relative_path.stem != "__init__":
                            parts.append(relative_path.stem)
                        # Construct full path: library.module.submodule.ClassName
                        module_path = ".".join([library_name, *parts])
                        return f"{module_path}.{class_name}"

            # Also check sys.path
            for sys_path in sys.path:
                if sys_path:
                    sys_path_obj = Path(sys_path)
                    if sys_path_obj.exists():
                        library_path = sys_path_obj / library_name
                        if library_path.exists() and source_path.is_relative_to(library_path):
                            relative_path = source_path.relative_to(library_path)
                            parts = list(relative_path.parts[:-1])
                            if relative_path.stem != "__init__":
                                parts.append(relative_path.stem)
                            module_path = ".".join([library_name, *parts])
                            return f"{module_path}.{class_name}"

            return None
        except Exception as e:
            logger.debug(
                f"Failed to construct full class path for {class_name} in {source_path}: {e}"
            )
            return None

    def _discover_library_sources(self, library_name: str) -> list[Path]:
        """Discover source files for a given library.

        Args:
            library_name: Name of the library (e.g., "panel")

        Returns:
            List of Python source file paths
        """
        if library_name in self.library_source_paths:
            return self.library_source_paths[library_name]

        source_paths = []

        # Search in site-packages directories
        for site_dir in [*site.getsitepackages(), site.getusersitepackages()]:
            if site_dir and Path(site_dir).exists():
                library_path = Path(site_dir) / library_name
                if library_path.exists():
                    source_paths.extend(self._collect_python_files(library_path))

        # Search in sys.path
        for sys_path in sys.path:
            if sys_path:
                sys_path_obj = Path(sys_path)
                if sys_path_obj.exists():
                    library_path = sys_path_obj / library_name
                    if library_path.exists():
                        source_paths.extend(self._collect_python_files(library_path))

        # Remove duplicates and cache
        unique_paths = list(set(source_paths))
        self.library_source_paths[library_name] = unique_paths

        logger.debug(f"Found {len(unique_paths)} source files for {library_name}")
        return unique_paths

    def _collect_python_files(self, directory: Path) -> list[Path]:
        """Recursively collect Python files from a directory.

        Args:
            directory: Directory to search

        Returns:
            List of Python file paths
        """
        python_files = []
        try:
            if directory.is_file() and directory.suffix == ".py":
                python_files.append(directory)
            elif directory.is_dir():
                python_files.extend(path for path in directory.rglob("*.py") if path.is_file())
        except (OSError, PermissionError) as e:
            logger.debug(f"Error accessing {directory}: {e}")

        return python_files

    def _find_class_in_file(
        self, source_path: Path, full_class_path: str, class_name: str
    ) -> ParameterizedInfo | None:
        """Find and analyze a specific class in a source file.

        Args:
            source_path: Path to Python source file
            full_class_path: Full class path for verification
            class_name: Name of the class to find

        Returns:
            ParameterizedInfo if class found and is Parameterized
        """
        # Check cache first
        if source_path in self.analyzed_files:
            file_classes = self.analyzed_files[source_path]
            if class_name in file_classes:
                return file_classes[class_name]

        try:
            # Read and parse the source file
            source_code = source_path.read_text(encoding="utf-8")
            tree = parso.parse(source_code)

            # Analyze the file
            file_analysis = self._analyze_file_ast(tree, source_code)
            self.analyzed_files[source_path] = file_analysis

            # Return the specific class if found
            return file_analysis.get(class_name)

        except Exception as e:
            logger.debug(f"Error parsing {source_path}: {e}")
            return None

    def _analyze_file_ast(
        self, tree: NodeOrLeaf, source_code: str
    ) -> dict[str, ParameterizedInfo | None]:
        """Analyze a parsed AST to find Parameterized classes.

        Args:
            tree: Parsed AST tree
            source_code: Original source code

        Returns:
            Dictionary mapping class names to ParameterizedInfo
        """
        imports: dict[str, str] = {}
        classes: dict[str, ParameterizedInfo | None] = {}

        # Parse imports first
        import_handler = ImportHandler(imports)
        self._walk_ast_for_imports(tree, import_handler)

        # Cache all class AST nodes for inheritance resolution
        self._cache_all_class_nodes(tree, imports)

        # Find and analyze classes
        self._walk_ast_for_classes(tree, imports, classes, source_code.split("\n"))

        return classes

    def _cache_all_class_nodes(self, node: NodeOrLeaf, imports: dict[str, str]) -> None:
        """Cache all class AST nodes for later inheritance resolution.

        Args:
            node: AST node to search
            imports: Import mappings for this file
        """
        if hasattr(node, "type") and node.type == "classdef":
            class_name = self._get_class_name(node)
            if class_name:
                # Store the class node and its imports context
                self.class_ast_cache[class_name] = (node, imports.copy())

        # Recursively cache children
        for child in parso_utils.get_children(node):
            self._cache_all_class_nodes(child, imports)

    def _walk_ast_for_imports(self, node: NodeOrLeaf, import_handler: ImportHandler) -> None:
        """Walk AST to find and parse import statements.

        Args:
            node: Current AST node
            import_handler: Handler for processing imports
        """
        if hasattr(node, "type"):
            if node.type == "import_name":
                import_handler.handle_import(node)
            elif node.type == "import_from":
                import_handler.handle_import_from(node)

        # Recursively walk children
        for child in parso_utils.get_children(node):
            self._walk_ast_for_imports(child, import_handler)

    def _walk_ast_for_classes(
        self,
        node: NodeOrLeaf,
        imports: dict[str, str],
        classes: dict[str, ParameterizedInfo | None],
        source_lines: list[str],
    ) -> None:
        """Walk AST to find and analyze class definitions.

        Args:
            node: Current AST node
            imports: Import mappings
            classes: Dictionary to store found classes
            source_lines: Source code lines for parameter extraction
        """
        if hasattr(node, "type") and node.type == "classdef":
            class_info = self._analyze_class_definition(node, imports, source_lines)
            if class_info:
                classes[class_info.name] = class_info

        # Recursively walk children
        for child in parso_utils.get_children(node):
            self._walk_ast_for_classes(child, imports, classes, source_lines)

    def _analyze_class_definition(
        self, class_node: NodeOrLeaf, imports: dict[str, str], source_lines: list[str]
    ) -> ParameterizedInfo | None:
        """Analyze a class definition to extract parameter information.

        Args:
            class_node: AST node representing class definition
            imports: Import mappings
            source_lines: Source code lines

        Returns:
            ParameterizedInfo if class is Parameterized, None otherwise
        """
        # Get class name
        class_name = self._get_class_name(class_node)
        if not class_name:
            return None

        # Check if class inherits from param.Parameterized
        if not self._inherits_from_parameterized(class_node, imports):
            return None

        # Create class info
        class_info = ParameterizedInfo(name=class_name)

        # Find parameter assignments in class body
        parameter_detector = ParameterDetector(imports)
        self._extract_class_parameters(
            class_node, parameter_detector, class_info, source_lines, imports
        )

        return class_info if class_info.parameters else None

    def _get_class_name(self, class_node: NodeOrLeaf) -> str | None:
        """Extract class name from class definition node.

        Args:
            class_node: Class definition AST node

        Returns:
            Class name or None if not found
        """
        for child in parso_utils.get_children(class_node):
            if child.type == "name":
                return parso_utils.get_value(child)
        return None

    def _inherits_from_parameterized(
        self, class_node: NodeOrLeaf, imports: dict[str, str]
    ) -> bool:
        """Check if a class inherits from param.Parameterized.

        Args:
            class_node: Class definition AST node
            imports: Import mappings

        Returns:
            True if class inherits from param.Parameterized
        """
        # First check direct inheritance
        base_classes = self._get_base_classes(class_node)

        for base_class in base_classes:
            if self._is_parameterized_base_class_name(base_class, imports):
                return True

            # For indirect inheritance, we need to resolve the base class
            # This would require deeper analysis across files, which is complex
            # For now, check some common patterns that we know inherit from Parameterized
            if self._is_known_parameterized_pattern(base_class, imports):
                return True

        return False

    def _get_base_classes(self, class_node: NodeOrLeaf) -> list[str]:
        """Extract base class names from class definition.

        Args:
            class_node: Class definition AST node

        Returns:
            List of base class names
        """
        base_classes = []
        in_parentheses = False

        for child in parso_utils.get_children(class_node):
            if child.type == "operator" and parso_utils.get_value(child) == "(":
                in_parentheses = True
            elif child.type == "operator" and parso_utils.get_value(child) == ")":
                in_parentheses = False
            elif in_parentheses:
                if child.type in ("name", "power", "atom_expr"):
                    base_class_name = self._resolve_base_class_name(child)
                    if base_class_name:
                        base_classes.append(base_class_name)
                elif child.type == "arglist":
                    # Handle multiple base classes in arglist
                    for arg_child in parso_utils.get_children(child):
                        if arg_child.type in ("name", "power", "atom_expr"):
                            base_class_name = self._resolve_base_class_name(arg_child)
                            if base_class_name:
                                base_classes.append(base_class_name)
                        elif (
                            arg_child.type == "operator"
                            and parso_utils.get_value(arg_child) == ","
                        ):
                            # Skip commas
                            pass

        return base_classes

    def _is_known_parameterized_pattern(self, base_class: str, imports: dict[str, str]) -> bool:
        """Check if a base class is a known pattern that inherits from Parameterized.

        This checks if the base class is already cached from the current file analysis,
        and if so, recursively checks its inheritance.

        Args:
            base_class: Base class name to check
            imports: Import mappings

        Returns:
            True if base class is known to inherit from Parameterized
        """
        # Avoid infinite recursion
        if not hasattr(self, "_inheritance_check_visited"):
            self._inheritance_check_visited = set()

        if base_class in self._inheritance_check_visited:
            return False

        self._inheritance_check_visited.add(base_class)

        try:
            # First check if this base class is already in our AST cache
            # (meaning it was found in the same file we're currently analyzing)
            class_info = self._find_class_definition(base_class)
            if class_info:
                class_definition, class_imports = class_info
                result = self._inherits_from_parameterized(class_definition, class_imports)
                return result

            # If not found in current file, try to resolve through imports
            if base_class in imports:
                import_path = imports[base_class]
                result = self._resolve_imported_class_inheritance(base_class, import_path, imports)
                return result

            return False
        finally:
            self._inheritance_check_visited.discard(base_class)

    def _resolve_inheritance_chain(self, class_name: str, imports: dict[str, str]) -> bool:
        """Resolve inheritance chain to check if it leads to param.Parameterized.

        Args:
            class_name: Name of the class to check
            imports: Import mappings from current file

        Returns:
            True if inheritance chain leads to param.Parameterized
        """
        # Direct check for param.Parameterized
        if class_name in ("param.Parameterized", "Parameterized"):
            return True

        # Check if class_name is imported and resolve it
        resolved_name = imports.get(class_name, class_name)
        return resolved_name == "param.Parameterized"

    def _find_class_definition(self, class_name: str) -> tuple[NodeOrLeaf, dict[str, str]] | None:
        """Find the AST node for a class definition.

        Args:
            class_name: Name of the class to find

        Returns:
            Tuple of (AST node, imports) of the class definition if found, None otherwise
        """
        # Check the AST cache first
        if class_name in self.class_ast_cache:
            return self.class_ast_cache[class_name]

        return None

    def _resolve_import_to_file_path(
        self, import_path: str, current_file_path: Path
    ) -> Path | None:
        """Resolve an import path to an actual file path.

        Args:
            import_path: Import path like "base.Widget" or "panel.widgets.base.Widget"
            current_file_path: Path of the file containing the import

        Returns:
            Absolute file path if found, None otherwise
        """
        if "." not in import_path:
            return None

        # Split import path into module and class
        parts = import_path.split(".")
        if len(parts) < 2:
            return None

        # The last part is the class name, everything else is the module path
        module_parts = parts[:-1]

        # For imports like "base.Widget", treat "base" as a relative import
        # since it's likely from the same directory
        if len(module_parts) == 1 and not module_parts[0].startswith(
            tuple(ALLOWED_EXTERNAL_LIBRARIES)
        ):
            return self._resolve_relative_import(module_parts, current_file_path)

        # Handle absolute imports within the same library
        return self._resolve_absolute_import(module_parts, current_file_path)

    def _resolve_relative_import(
        self, module_parts: list[str], current_file_path: Path
    ) -> Path | None:
        """Resolve a relative import like ['base'] from current file location.

        Args:
            module_parts: Module parts like ['base'] or ['..', 'core']
            current_file_path: Current file path

        Returns:
            Resolved file path or None
        """
        # Start from the directory containing the current file
        base_dir = current_file_path.parent

        # Handle relative import levels
        for part in module_parts:
            if part == "..":
                base_dir = base_dir.parent
            elif part == ".":
                continue  # Stay in current directory
            else:
                # This is the actual module name
                potential_file = base_dir / f"{part}.py"
                if potential_file.exists():
                    return potential_file

                # Try as a package
                potential_package = base_dir / part / "__init__.py"
                if potential_package.exists():
                    return potential_package

        return None

    def _resolve_absolute_import(
        self, module_parts: list[str], current_file_path: Path
    ) -> Path | None:
        """Resolve an absolute import within the same library.

        Args:
            module_parts: Module parts like ['panel', 'widgets', 'base']
            current_file_path: Current file path for context

        Returns:
            Resolved file path or None
        """
        # Find the library root by examining the current file path
        library_root = self._find_library_root(current_file_path)
        if not library_root:
            return None

        # Build path from library root
        potential_path = library_root
        for part in module_parts[1:]:  # Skip the first part (library name)
            potential_path = potential_path / part

        # Try as a module file
        module_file = potential_path.with_suffix(".py")
        if module_file.exists():
            return module_file

        # Try as a package
        package_file = potential_path / "__init__.py"
        if package_file.exists():
            return package_file

        return None

    def _find_library_root(self, file_path: Path) -> Path | None:
        """Find the root directory of the library containing the given file.

        Args:
            file_path: Path to a file within the library

        Returns:
            Library root directory or None
        """
        # Walk up the directory tree looking for a known library name
        current_dir = file_path.parent
        while current_dir != current_dir.parent:  # Not at filesystem root
            if current_dir.name in ALLOWED_EXTERNAL_LIBRARIES:
                return current_dir
            current_dir = current_dir.parent

        return None

    def _parse_import_statement(
        self, import_path: str, imported_name: str
    ) -> tuple[str, str] | None:
        """Parse an import statement to extract module path and class name.

        Args:
            import_path: Import path from imports dict
            imported_name: The imported name

        Returns:
            Tuple of (module_path, class_name) or None
        """
        if "." in import_path:
            # Handle cases like "base.Widget" -> ("base", "Widget")
            parts = import_path.split(".")
            return ".".join(parts[:-1]), parts[-1]
        else:
            # Direct import like "Widget" -> no module path, return None
            return None

    def _queue_file_for_analysis(self, file_path: Path, reason: str) -> None:
        """Add a file to the analysis queue if not already analyzed.

        Args:
            file_path: Path to the file to analyze
            reason: Reason for analysis (for debugging)
        """
        if file_path not in self.analyzed_files and file_path not in self.currently_analyzing:
            self.analysis_queue.append((file_path, reason))
            logger.debug(f"Queued {file_path} for analysis: {reason}")

    def _process_analysis_queue(self) -> None:
        """Process all files in the analysis queue."""
        while self.analysis_queue:
            file_path, reason = self.analysis_queue.pop(0)

            # Skip if already analyzing (circular dependency protection)
            if file_path in self.currently_analyzing:
                continue

            # Skip if already analyzed
            if file_path in self.analyzed_files:
                continue

            try:
                self.currently_analyzing.add(file_path)
                logger.debug(f"Analyzing {file_path}: {reason}")

                # Read and parse the file
                source_code = file_path.read_text(encoding="utf-8")
                source_lines = source_code.split("\n")
                tree = parso.parse(source_code)

                # Store source lines for parameter extraction
                self.file_source_cache[file_path] = source_lines

                # Analyze the file (this may queue additional files)
                file_analysis = self._analyze_file_ast(tree, source_code)
                self.analyzed_files[file_path] = file_analysis

                logger.debug(
                    f"Completed analysis of {file_path}, found {len(file_analysis)} classes"
                )

            except Exception as e:
                logger.debug(f"Failed to analyze {file_path}: {e}")
                # Mark as analyzed even if failed to prevent retry loops
                self.analyzed_files[file_path] = {}
            finally:
                self.currently_analyzing.discard(file_path)

    def _cleanup_ast_caches(self) -> None:
        """Clean up AST caches to reduce memory usage and garbage collection delay.

        This method clears the internal caches that hold AST nodes and source code
        after analysis is complete, which helps reduce memory usage and speeds up
        process cleanup by reducing the amount of data that needs to be garbage collected.
        """
        logger.debug(
            f"Cleaning up AST caches: {len(self.class_ast_cache)} AST nodes, "
            f"{len(self.file_source_cache)} source files, "
            f"{len(self.analyzed_files)} analyzed files"
        )

        # Clear the AST cache that holds parsed AST nodes
        self.class_ast_cache.clear()

        # Clear the source file cache
        self.file_source_cache.clear()

        # Clear analyzed files cache
        self.analyzed_files.clear()

        logger.debug("AST cache cleanup completed")

    def _convert_ast_to_class_info(
        self,
        class_node: NodeOrLeaf,
        imports: dict[str, str],
        full_class_path: str,
        file_path: Path,
    ) -> ParameterizedInfo:
        """Convert an AST class node to ParameterizedInfo.

        Args:
            class_node: AST node of the class
            imports: Import mappings
            full_class_path: Full path like "panel.widgets.IntSlider"

        Returns:
            ParameterizedInfo with extracted parameters
        """
        class_name = self._get_class_name(class_node)
        if not class_name:
            msg = "Could not extract class name from AST node"
            raise ValueError(msg)

        # Create class info
        class_info = ParameterizedInfo(name=class_name)

        # Find parameter assignments in class body
        from param_lsp._analyzer.ast_navigator import ParameterDetector

        parameter_detector = ParameterDetector(imports)

        # Get the actual source lines for parameter extraction
        source_lines = self.file_source_cache.get(file_path)
        if source_lines is None:
            # If not in cache, read the file directly
            try:
                source_code = file_path.read_text(encoding="utf-8")
                source_lines = source_code.split("\n")
                # Cache it for future use
                self.file_source_cache[file_path] = source_lines
            except Exception as e:
                logger.error(f"Failed to read source file {file_path}: {e}")
                source_lines = [""]  # Minimal fallback, not 1000 empty lines

        self._extract_class_parameters(
            class_node, parameter_detector, class_info, source_lines, imports
        )

        # Also extract parameters from parent classes within the same file
        self._extract_inherited_parameters(
            class_node, parameter_detector, class_info, source_lines, imports
        )

        return class_info

    def _extract_inherited_parameters(
        self,
        class_node: NodeOrLeaf,
        parameter_detector: ParameterDetector,
        class_info: ParameterizedInfo,
        source_lines: list[str],
        imports: dict[str, str],
    ) -> None:
        """Extract parameters from parent classes within the same file.

        Args:
            class_node: Class definition AST node
            parameter_detector: Detector for parameter assignments
            class_info: Class info to populate with inherited parameters
            source_lines: Source code lines
            imports: Import mappings
        """
        # Get direct parent classes
        base_classes = self._get_base_classes(class_node)

        for base_class in base_classes:
            # Look for parent class definition in the same file (class_ast_cache)
            parent_info = self._find_class_definition(base_class)
            if parent_info:
                parent_node, parent_imports = parent_info

                # Extract parameters from parent class
                parent_class_info = ParameterizedInfo(name=base_class)
                self._extract_class_parameters(
                    parent_node,
                    parameter_detector,
                    parent_class_info,
                    source_lines,
                    parent_imports,
                )

                # Add parent parameters to child (child parameters take precedence)
                for param_name, param_info in parent_class_info.parameters.items():
                    if param_name not in class_info.parameters:
                        class_info.parameters[param_name] = param_info

                # Recursively check parent's parents
                self._extract_inherited_parameters(
                    parent_node, parameter_detector, class_info, source_lines, parent_imports
                )

    def _resolve_imported_class_inheritance(
        self, class_name: str, import_path: str, context_imports: dict[str, str]
    ) -> bool:
        """Resolve inheritance for an imported class by analyzing its source file.

        Args:
            class_name: Name of the imported class
            import_path: Import path like "base.Widget"
            context_imports: Import context from current file

        Returns:
            True if the imported class inherits from Parameterized
        """
        # First check if it's clearly not a Parameterized class
        if import_path.startswith(_STDLIB_MODULES):
            return False

        # Get the current file context (we need this for import resolution)
        current_file = self._get_current_file_from_context()
        if not current_file:
            logger.debug(f"Could not determine current file context for {class_name}")
            return False

        # Resolve the import to a file path
        target_file = self._resolve_import_to_file_path(import_path, current_file)
        if not target_file:
            logger.debug(f"Could not resolve import {import_path} to file path")
            return False

        # Queue the target file for analysis
        self._queue_file_for_analysis(target_file, f"resolving inheritance for {class_name}")

        # Process the queue to analyze the file
        self._process_analysis_queue()

        # Now check if we can find the class and its inheritance
        parsed_class_name = import_path.split(".")[-1]  # Extract actual class name
        class_info = self._find_class_definition(parsed_class_name)
        if class_info:
            class_definition, class_imports = class_info
            result = self._inherits_from_parameterized(class_definition, class_imports)
            return result

        # If we can't resolve the inheritance chain, return False
        # This is more honest than guessing based on module names
        logger.error(f"Could not resolve inheritance for {import_path} - static analysis failed")
        return False

    def _get_current_file_from_context(self) -> Path | None:
        """Get the current file being analyzed from context.

        This is a helper method to determine which file we're currently analyzing
        for import resolution purposes.

        Returns:
            Path to current file or None if not determinable
        """
        # Look for the most recently added file to the analysis queue or currently analyzing
        if self.currently_analyzing:
            return next(iter(self.currently_analyzing))

        # If nothing is currently being analyzed, we might be in the initial phase
        # In this case, we'll need to track this differently
        # For now, return None and rely on heuristics
        return None

    def _search_for_class_in_ast(
        self, node: NodeOrLeaf, target_class_name: str
    ) -> NodeOrLeaf | None:
        """Recursively search for a class definition in an AST.

        Args:
            node: Current AST node to search
            target_class_name: Name of the class to find

        Returns:
            AST node of the class definition if found, None otherwise
        """
        if hasattr(node, "type") and node.type == "classdef":
            class_name = self._get_class_name(node)
            if class_name == target_class_name:
                return node

        # Recursively search children
        for child in parso_utils.get_children(node):
            result = self._search_for_class_in_ast(child, target_class_name)
            if result:
                return result

        return None

    def _is_parameterized_base_class_name(
        self, base_class_name: str, imports: dict[str, str]
    ) -> bool:
        """Check if a base class name represents param.Parameterized.

        Args:
            base_class_name: Name of the base class
            imports: Import mappings

        Returns:
            True if base class is param.Parameterized
        """
        # Check direct reference
        if base_class_name == "param.Parameterized":
            return True

        # Check imports
        if base_class_name in imports:
            full_name = imports[base_class_name]
            if full_name == "param.Parameterized":
                return True

        return False

    def _resolve_base_class_name(self, node: NodeOrLeaf) -> str | None:
        """Resolve base class name from AST node.

        Args:
            node: AST node representing base class reference

        Returns:
            Resolved base class name
        """
        if node.type == "name":
            return parso_utils.get_value(node)
        elif node.type in ("power", "atom_expr"):
            # Handle dotted names like param.Parameterized
            parts = []
            for child in parso_utils.get_children(node):
                if child.type == "name":
                    parts.append(parso_utils.get_value(child))
                elif child.type == "trailer":
                    parts.extend(
                        parso_utils.get_value(trailer_child)
                        for trailer_child in parso_utils.get_children(child)
                        if trailer_child.type == "name"
                    )
            return ".".join(parts) if parts else None
        return None

    def _extract_class_parameters(
        self,
        class_node: NodeOrLeaf,
        parameter_detector: ParameterDetector,
        class_info: ParameterizedInfo,
        source_lines: list[str],
        imports: dict[str, str],
    ) -> None:
        """Extract parameter assignments from class body.

        Args:
            class_node: Class definition AST node
            parameter_detector: Detector for parameter assignments
            class_info: Class info to populate with parameters
            source_lines: Source code lines for extracting definitions
        """
        # Find class suite (body)
        suite_node = None
        for child in parso_utils.get_children(class_node):
            if child.type == "suite":
                suite_node = child
                break

        if not suite_node:
            return

        # Walk through statements in class body
        self._walk_class_body(suite_node, parameter_detector, class_info, source_lines, imports)

    def _walk_class_body(
        self,
        suite_node: NodeOrLeaf,
        parameter_detector: ParameterDetector,
        class_info: ParameterizedInfo,
        source_lines: list[str],
        imports: dict[str, str],
    ) -> None:
        """Walk through class body to find parameter assignments.

        Args:
            suite_node: Suite AST node containing class body
            parameter_detector: Detector for parameter assignments
            class_info: Class info to populate
            source_lines: Source code lines
        """
        for child in parso_utils.get_children(suite_node):
            if child.type == "simple_stmt":
                # Check for assignment statements
                for stmt_child in parso_utils.get_children(child):
                    if (
                        stmt_child.type == "expr_stmt"
                        and parameter_detector.is_parameter_assignment(stmt_child)
                    ):
                        param_info = self._extract_parameter_info(
                            stmt_child, source_lines, imports
                        )
                        if param_info:
                            class_info.add_parameter(param_info)
            elif hasattr(child, "type") and child.type not in (
                "funcdef",
                "async_funcdef",
                "classdef",
            ):
                # Recursively search in nested structures, but skip function/method definitions
                # and nested class definitions to avoid treating method-local variables as parameters
                self._walk_class_body(child, parameter_detector, class_info, source_lines, imports)

    def _extract_parameter_info(
        self, assignment_node: NodeOrLeaf, source_lines: list[str], imports: dict[str, str]
    ) -> ParameterInfo | None:
        """Extract parameter information from an assignment statement.

        Args:
            assignment_node: Assignment AST node
            source_lines: Source code lines

        Returns:
            ParameterInfo if extraction successful
        """
        # Get parameter name (left side of assignment)
        param_name = self._get_parameter_name(assignment_node)
        if not param_name:
            return None

        # Use existing parameter extractor with source content
        source_content = "\n".join(source_lines)

        # Use the imports from the file analysis

        return extract_parameter_info_from_assignment(
            assignment_node, param_name, imports, source_content
        )

    def _get_parameter_name(self, assignment_node: NodeOrLeaf) -> str | None:
        """Extract parameter name from assignment node.

        Args:
            assignment_node: Assignment AST node

        Returns:
            Parameter name or None
        """
        # Find the name before the '=' operator
        for child in parso_utils.get_children(assignment_node):
            if child.type == "name":
                return parso_utils.get_value(child)
            elif child.type == "operator" and parso_utils.get_value(child) == "=":
                break
        return None

    def _resolve_base_class_paths(
        self, class_node: NodeOrLeaf, file_imports: dict[str, str], library_name: str
    ) -> list[str]:
        """Resolve base class names to full paths using imports.

        Args:
            class_node: Class definition AST node
            file_imports: Import mappings for this file
            library_name: Name of the library (e.g., "panel")

        Returns:
            List of full base class paths
        """
        base_classes = self._get_base_classes(class_node)
        full_bases = []

        for base in base_classes:
            if "." in base:
                # Already qualified: "panel.layout.ListPanel"
                full_bases.append(base)
            elif base in file_imports:
                # Resolve via imports: ListPanel -> panel.layout.base.ListPanel
                full_bases.append(file_imports[base])
            else:
                # Assume same module - this is a simplification
                # In reality, we'd need to check if it's defined in the same file
                # For now, we'll just use the base name as-is and let the iterative
                # resolution handle it if it's in the same file
                full_bases.append(base)

        return full_bases

    def _is_parameterized_base(self, base_path: str) -> bool:
        """Check if a base class path is param.Parameterized.

        Args:
            base_path: Base class path to check

        Returns:
            True if base class is param.Parameterized
        """
        return base_path in (
            "param.Parameterized",
            "Parameterized",  # if imported as "from param import Parameterized"
        )

    def _base_matches_parameterized_class(
        self, base_name: str, parameterized_classes: set[str]
    ) -> bool:
        """Check if a base class name matches any known Parameterized class.

        Handles matching both simple names (e.g., 'ListPanel') and full paths
        (e.g., 'panel.layout.base.ListPanel').

        Args:
            base_name: Base class name to check (may be simple or fully qualified)
            parameterized_classes: Set of full paths to known Parameterized classes

        Returns:
            True if base_name matches a known Parameterized class
        """
        # Direct match: base_name is a full path
        if base_name in parameterized_classes:
            return True

        # Partial match: base_name is a simple name that matches the last component
        # of a full path (e.g., 'ListPanel' matches 'panel.layout.base.ListPanel')
        if "." not in base_name:
            for full_path in parameterized_classes:
                if full_path.endswith(f".{base_name}"):
                    return True

        return False
