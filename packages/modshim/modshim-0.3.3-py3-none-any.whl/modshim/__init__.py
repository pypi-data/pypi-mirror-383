"""modshim: A module that combines two modules by rewriting their ASTs.

This module allows "shimming" one module on top of another, creating a combined module
that includes functionality from both. Internal imports are redirected to the mount point.
"""

from __future__ import annotations

import ast
import logging
import marshal
import os
import os.path
import sys
import threading
from importlib import import_module
from importlib.abc import InspectLoader, Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from importlib.util import find_spec, module_from_spec
from pathlib import Path
from types import CodeType, ModuleType
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Sequence

# Set up logger with NullHandler
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
if os.getenv("MODSHIM_DEBUG"):
    logging.basicConfig(level=logging.DEBUG)


class _ModuleReferenceRewriter(ast._Unparser, ast.NodeTransformer):  #  pyright: ignore[reportAttributeAccessIssue]
    """AST transformer that rewrites module references to point to the mount point."""

    search: str
    replace: str
    dirty: bool = False

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """Rewrite 'from X import Y' statements."""
        # If this is an import from the original module or its submodules,
        # rewrite it to import from the mount point
        if node.module and (
            node.module == self.search or node.module.startswith(f"{self.search}.")
        ):
            # Replace the original module name with the mount point
            if node.module == self.search:
                new_module = self.replace
            else:
                # Handle submodule imports
                suffix = node.module[len(self.search) :]
                new_module = f"{self.replace}{suffix}"

            self.dirty = True
            node = ast.ImportFrom(module=new_module, names=node.names, level=node.level)
        return super().visit_ImportFrom(node)

    def visit_Import(self, node: ast.Import) -> ast.Import:
        """Rewrite 'import X' statements."""
        new_names: list[ast.alias] = []
        for name in node.names:
            if name.name == self.search:
                # Replace the original module name with the mount point
                new_names.append(ast.alias(name=self.replace, asname=name.asname))
            elif name.name.startswith(f"{self.search}."):
                # Handle submodule imports
                suffix = name.name[len(self.search) :]
                new_name = f"{self.replace}{suffix}"
                new_names.append(ast.alias(name=new_name, asname=name.asname))
            else:
                new_names.append(name)

        if new_names:
            self.dirty = True
            node = ast.Import(names=new_names)
        return super().visit_Import(node)

    def visit_Attribute(self, node: ast.AST) -> ast.AST:
        """Rewrite module references like 'urllib.response' to 'urllib_punycode.response'."""
        # First visit any child nodes
        # node = self.generic_visit(node)

        # Check if this is a reference to the original module
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == self.search
        ):
            # Replace the module name with the mount point
            self.dirty = True
            node = ast.Attribute(
                value=ast.Name(id=self.replace, ctx=node.value.ctx),
                attr=node.attr,
                ctx=node.ctx,
            )
            return super().visit_Attribute(node)

        # Check for nested attributes like urllib.parse.urlparse
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute):
            # Build the full attribute chain to check if it starts with the original module
            attrs: list[tuple[str, ast.expr_context]] = []
            current = node
            while isinstance(current, ast.Attribute):
                attrs.insert(0, (current.attr, current.ctx))
                current = current.value

            # If the base is the original module name, rewrite the entire chain
            if isinstance(current, ast.Name) and current.id == self.search:
                # Start with the mount point as the base
                result = ast.Name(id=self.replace, ctx=current.ctx)
                # Rebuild the attribute chain
                for attr, ctx in attrs:
                    result = ast.Attribute(value=result, attr=attr, ctx=ctx)

                self.dirty = True

        return super().visit_Attribute(node)


def reference_rewrite_factory(
    search: str, replace: str
) -> type[_ModuleReferenceRewriter]:
    """Get an AST module reference rewriter and unparser."""

    class ReferenceRewriter(_ModuleReferenceRewriter): ...

    ReferenceRewriter.search = search
    ReferenceRewriter.replace = replace

    return ReferenceRewriter


def get_module_source(module_name: str, spec: ModuleSpec) -> str | None:
    """Get the source code of a module using its loader.

    Args:
        module_name: Name of the module
        spec: The module's spec

    Returns:
        The source code of the module or None if not available
    """
    if not spec or not spec.loader or not isinstance(spec.loader, InspectLoader):
        return None

    try:
        # Try to get the source directly
        return spec.loader.get_source(module_name)
    except (ImportError, AttributeError):
        return None


def get_cache_path(
    upper_file_path: str,
    mount_root: str,
    original_module_name: str,
    *,
    optimization: str | int | None = None,
) -> Path:
    """Given the path to a .py file, return the path to its .pyc file.

    The .py file does not need to exist; this simply returns the path to the
    .pyc file calculated as if the .py file were imported. All files are
    cached in the upper files' __modshim__ directory.

    The 'optimization' parameter controls the presumed optimization level of
    the bytecode file. If 'optimization' is not None, the string representation
    of the argument is taken and verified to be alphanumeric (else ValueError
    is raised).

    If sys.implementation.cache_tag is None then NotImplementedError is raised.
    """
    upper_path = Path(upper_file_path)
    cache_dir = upper_path.parent / "__modshim__"

    tag = sys.implementation.cache_tag
    if tag is None:
        raise NotImplementedError("sys.implementation.cache_tag is None")

    base_filename = f"{mount_root}.{original_module_name}"
    stem = f"{base_filename}.{tag}"

    if optimization is None and (
        optimization := str(sys.flags.optimize if sys.flags.optimize != 0 else "")
    ):
        if not optimization.isalnum():
            raise ValueError(f"{optimization!r} is not alphanumeric")
        stem = f"{stem}._OPT{optimization}"

    filename = cache_dir / f"{stem}.pyc"
    return filename


class ModShimLoader(Loader):
    """Loader for shimmed modules."""

    # Track module that have already been created
    cache: ClassVar[dict[tuple[str, str], ModuleType]] = {}
    # Store magic number at class level
    _magic_number = (1234).to_bytes(2, "little") + b"\r\n"

    # Track modules that are currently being processed to detect circular shimming
    _processing: ClassVar[set[ModuleType]] = set()

    def __init__(
        self,
        lower_spec: ModuleSpec | None,
        upper_spec: ModuleSpec | None,
        lower_root: str,
        upper_root: str,
        mount_root: str,
        finder: ModShimFinder,
    ) -> None:
        """Initialize the loader.

        Args:
            lower_spec: The module spec for the lower module
            upper_spec: The module spec for the upper module
            lower_root: The root package name of the lower module
            upper_root: The root package name of the upper module
            mount_root: The root mount point for import rewriting
            finder: The ModShimFinder instance that created this loader
        """
        self.lower_spec: ModuleSpec | None = lower_spec
        self.upper_spec: ModuleSpec | None = upper_spec
        self.lower_root: str = lower_root
        self.upper_root: str = upper_root
        self.mount_root: str = mount_root
        self.finder: ModShimFinder = finder

        # Set flag indicating we are performing an internal lookup
        finder._internal_call.active = True
        try:
            try:
                upper_root_spec = find_spec(upper_root)
            except (ImportError, AttributeError):
                upper_root_spec = None
            self.upper_root_origin = upper_root_spec.origin if upper_root_spec else None
        finally:
            # Unset the internal call flag
            finder._internal_call.active = False

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        """Create a new module object."""
        key = spec.name, self.mount_root
        if key in self.cache:
            log.debug("Returning cached module %r", spec.name)
            return self.cache[key]

        module = ModuleType(spec.name)
        module.__file__ = f"<{spec.name}>"
        module.__loader__ = self
        module.__package__ = spec.parent

        # If this is a package, set up package attributes
        if spec.submodule_search_locations is not None:
            module.__path__ = list(spec.submodule_search_locations)

        # Store in cache
        # with self.finder._cache_lock:
        self.cache[key] = module

        return module

    def rewrite_module_code(
        self, code: str, search: str, replace: str
    ) -> tuple[str, bool]:
        """Rewrite imports and module references in module code.

        Args:
            code: The source code to rewrite
            search: The root package name to search for
            replace: The root package name to replace with

        Returns:
            Tuple of the rewritten source code and a bool signifying if any
                modifications have been made
        """
        tree = ast.parse(code)

        # Use the new transformer that handles both imports and module references
        transformer = reference_rewrite_factory(search, replace)()
        new_code = transformer.visit(tree)
        if not transformer.dirty:
            return code, False
        return new_code, True

    def _get_cached_code(self, spec: ModuleSpec) -> CodeType | None:
        """Get cached compiled code if it exists and is valid."""
        origin = spec.origin
        upper_origin = self.upper_root_origin
        if not origin or origin.startswith("<") or not upper_origin:
            return None

        source_path = Path(origin)

        # Create cache filename that includes the mount point to avoid conflicts
        cache_path = get_cache_path(
            upper_file_path=upper_origin,
            mount_root=self.mount_root,
            original_module_name=spec.name,
        )
        if not cache_path.exists():
            return None

        try:
            source_stat = source_path.stat()
        except OSError:
            return None

        # Check if cache exists and is newer than source
        if cache_path.stat().st_mtime <= source_stat.st_mtime:
            return None

        # Read and validate cache
        with cache_path.open("rb") as f:
            # Read magic number and timestamp
            magic = f.read(4)
            if magic != self._magic_number:
                return None

            cached_mtime_bytes = f.read(4)
            cached_size_bytes = f.read(4)
            if len(cached_mtime_bytes) != 4 or len(cached_size_bytes) != 4:
                return None

            source_mtime = int(source_stat.st_mtime)
            source_size = source_stat.st_size
            if int.from_bytes(cached_mtime_bytes, "little") != (
                source_mtime & 0xFFFFFFFF
            ) or int.from_bytes(cached_size_bytes, "little") != (
                source_size & 0xFFFFFFFF
            ):
                return None

            # Load code object
            return marshal.load(f)  # noqa: S302

    def _cache_code(self, spec: ModuleSpec, code_obj: CodeType) -> None:
        """Cache compiled code to disk."""
        origin = spec.origin
        upper_origin = self.upper_root_origin

        if not origin or origin.startswith("<") or not upper_origin:
            return None

        try:
            source_path = Path(origin)
            source_stat = source_path.stat()
        except OSError:
            # Cannot get source stats, so cannot cache.
            return

        source_mtime = int(source_stat.st_mtime)
        source_size = source_stat.st_size

        # Get cache path
        cache_path = get_cache_path(
            upper_file_path=upper_origin,
            mount_root=self.mount_root,
            original_module_name=spec.name,
        )
        # Ensure cache directory exists
        cache_path.parent.mkdir(exist_ok=True, parents=True)

        # Write cache file
        try:
            with cache_path.open("wb") as f:
                # Write magic number and timestamp/size
                f.write(self._magic_number)
                f.write((source_mtime & 0xFFFFFFFF).to_bytes(4, "little"))
                f.write((source_size & 0xFFFFFFFF).to_bytes(4, "little"))

                # Write code object
                marshal.dump(code_obj, f)
        except OSError:
            # Ignore cache write failures
            pass

    def exec_module(self, module: ModuleType) -> None:
        """Execute the module by combining upper and lower modules."""
        log.debug("Exec_module called for %r", module.__name__)

        # Check if we're in a circular shimming situation
        if module in self._processing:
            return
        # Mark this module as being processed to detect circular shimming
        self._processing.add(module)

        # Calculate upper and lower names
        lower_name = module.__name__.replace(self.mount_root, self.lower_root)
        upper_name = module.__name__.replace(self.mount_root, self.upper_root)

        if lower_spec := self.lower_spec:
            lower_filename = f"modshim://{module.__file__}::{lower_spec.origin}"
            lower_source: str | None = None

            # Try to get cached code first
            code_obj = None
            if lower_spec.origin:
                code_obj = self._get_cached_code(lower_spec)

            def _get_lower_source() -> str | None:
                if source := get_module_source(lower_name, lower_spec):
                    source, _ = self.rewrite_module_code(
                        source, self.lower_root, self.mount_root
                    )
                return source

            if code_obj is None:
                lower_source = _get_lower_source()

                if lower_source is not None:
                    # Cache miss - get and rewrite the source
                    code_obj = compile(lower_source, lower_filename, "exec")

                    # self.cache_code(code_obj, lower_source, lower_spec)
                    if lower_spec.origin:
                        self._cache_code(lower_spec, code_obj)

            if code_obj is not None:
                try:
                    log.debug("Executing lower: %r", self.lower_spec.name)
                    exec(code_obj, module.__dict__)  # noqa: S102
                except:
                    if lower_source is None:
                        lower_source = _get_lower_source()
                    if lower_source is not None:
                        import linecache

                        # Add the source to the line cache on error for better error reporting
                        linecache.cache[lower_filename] = (
                            len(lower_source),
                            None,
                            lower_source.splitlines(True),
                            lower_filename,
                        )
                    raise

            # If all else fails, execute the lower module natively then copy its attributes
            elif lower_spec.loader:
                lower_module = module_from_spec(lower_spec)
                lower_spec.loader.exec_module(lower_module)
                # Copy attributes
                module.__dict__.update(
                    {
                        k: v
                        for k, v in lower_module.__dict__.items()
                        if not k.startswith("__")
                    }
                )
        else:
            log.debug("No lower spec to execute")

        # Load and execute upper module
        if upper_spec := self.upper_spec:
            # Generate name of working module
            parts = module.__name__.split(".")
            working_name = ".".join([*parts[:-1], f"_working_{parts[-1]}"])
            # Create a working copy of the module's state after executing the lower module
            working_module = ModuleType(working_name)
            working_module.__name__ = working_name
            working_module.__file__ = getattr(module, "__file__", None)
            working_module.__package__ = getattr(module, "__package__", None)
            # Copy module state to working module
            working_module.__dict__.update(module.__dict__)
            # Register the modules in sys.modules
            sys.modules[working_name] = working_module

            upper_filename = f"modshim://{module.__file__}::{upper_spec.origin}"
            upper_source: str | None = None

            # Try to get cached code first
            code_obj = None
            if upper_spec.origin:
                code_obj = self._get_cached_code(upper_spec)

            def _get_upper_source() -> str | None:
                if source := get_module_source(upper_name, upper_spec):
                    # Rewrite imports of lower to mount
                    source, _ = self.rewrite_module_code(
                        source, self.lower_root, self.mount_root
                    )
                    # Rewrite import of the current module to the working module to prevent
                    # recursion errors
                    source, _ = self.rewrite_module_code(
                        source, module.__name__, working_name
                    )
                return source

            if code_obj is None:
                # Cache miss - get and rewrite the source
                upper_source = _get_upper_source()

                if upper_source is not None:
                    # Execute the code with the filename that matches the line cache entry
                    code_obj = compile(upper_source, upper_filename, "exec")

                    if upper_spec.origin:
                        self._cache_code(upper_spec, code_obj)

            if code_obj is not None:
                try:
                    log.debug("Executing upper: %r", self.upper_spec.name)
                    exec(code_obj, module.__dict__)  # noqa: S102
                except:
                    if upper_source is None:
                        upper_source = _get_upper_source()
                    if upper_source is not None:
                        import linecache

                        # Add the source to the line cache on error for better error reporting
                        linecache.cache[upper_filename] = (
                            len(upper_source),
                            None,
                            upper_source.splitlines(True),
                            upper_filename,
                        )
                    raise

            elif upper_spec.loader and isinstance(upper_spec.loader, InspectLoader):
                # Fall back to compiled code if source is not available
                try:
                    upper_code = upper_spec.loader.get_code(upper_name)
                    if upper_code:
                        exec(upper_code, module.__dict__)  # noqa: S102

                except (ImportError, AttributeError):
                    pass
        else:
            log.debug("No upper spec to execute")

        # Remove this module from processing set
        self._processing.discard(module)

        log.debug("Exec_module completed for %r", module.__name__)


class ModShimFinder(MetaPathFinder):
    """Finder for shimmed modules."""

    # Dictionary mapping mount points to (upper_module, lower_module) tuples
    _mappings: ClassVar[dict[str, tuple[str, str]]] = {}
    # Thread-local storage to track internal find_spec calls
    _internal_call: ClassVar[threading.local] = threading.local()

    @classmethod
    def register_mapping(
        cls, mount_root: str, upper_root: str, lower_root: str
    ) -> None:
        """Register a new module mapping.

        Args:
            lower_root: The name of the lower module
            upper_root: The name of the upper module
            mount_root: The name of the mount point
        """
        cls._mappings[mount_root] = (upper_root, lower_root)

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        """Find a module spec for the given module name."""
        log.debug("Find spec called for %r", fullname)

        # If this find_spec is called internally from _create_spec, ignore it
        # to allow standard finders to locate the original lower/upper modules.
        if getattr(self._internal_call, "active", False):
            return None

        # Check if this is a direct mount point
        if fullname in self._mappings:
            upper_root, lower_root = self._mappings[fullname]
            # if fullname != upper_root and fullname != lower_root:
            # if fullname != lower_root:
            return self._create_spec(fullname, upper_root, lower_root, fullname)

        # Check if this is a submodule of a mount point
        for mount_root, (upper_root, lower_root) in self._mappings.items():
            # if fullname.startswith(f"{mount_root}."):
            if fullname.startswith(f"{mount_root}."):
                # if not (fullname.startswith((f"{upper_root}.", f"{lower_root}."))):
                return self._create_spec(fullname, upper_root, lower_root, mount_root)

        return None

    def _create_spec(
        self, fullname: str, upper_root: str, lower_root: str, mount_root: str
    ) -> ModuleSpec:
        """Create a module spec for the given module name."""
        # Calculate full lower and upper names
        lower_name = fullname.replace(mount_root, lower_root)
        upper_name = fullname.replace(mount_root, upper_root)

        # Set flag indicating we are performing an internal lookup
        self._internal_call.active = True
        try:
            # Find upper and lower specs using standard finders
            # (Our finder will ignore calls while _internal_call.active is True)
            try:
                log.debug("Finding lower spec %r", lower_name)
                lower_spec = find_spec(lower_name)
            except (ImportError, AttributeError):
                lower_spec = None
            log.debug("Found lower spec %r", lower_spec)
            try:
                log.debug("Finding upper spec %r", upper_name)
                upper_spec = find_spec(upper_name)
            except (ImportError, AttributeError):
                upper_spec = None
            log.debug("Found upper spec %r", upper_spec)

        finally:
            # Unset the internal call flag
            self._internal_call.active = False

        # Raise ImportError if neither module exists
        if lower_spec is None and upper_spec is None:
            raise ImportError(
                f"Cannot find module '{fullname}' (tried '{lower_name}' and '{upper_name}')"
            )

        # Create loader and spec using the correctly found specs
        loader = ModShimLoader(
            lower_spec, upper_spec, lower_root, upper_root, mount_root, finder=self
        )
        spec = ModuleSpec(
            name=fullname,
            loader=loader,
            origin=upper_spec.origin if upper_spec else None,
            is_package=lower_spec.submodule_search_locations is not None
            if lower_spec
            else False,
        )

        # Add upper module submodule search locations first
        if upper_spec and upper_spec.submodule_search_locations is not None:
            spec.submodule_search_locations = [
                *(spec.submodule_search_locations or []),
                *list(upper_spec.submodule_search_locations),
            ]

        # Add lower module submodule search locations to fall back on
        # if lower_spec and lower_spec.submodule_search_locations is not None:
        #     spec.submodule_search_locations = [
        #         *(spec.submodule_search_locations or []),
        #         *list(lower_spec.submodule_search_locations),
        #     ]
        return spec


# Thread-local storage to track function execution state
_shim_state = threading.local()


def shim(lower: str, upper: str = "", mount: str = "") -> None:
    """Mount an upper module or package on top of a lower module or package.

    This function sets up import machinery to dynamically combine modules
    from the upper and lower packages when they are imported through
    the mount point.

    Args:
        upper: The name of the upper module or package
        lower: The name of the lower module or package
        mount: The name of the mount point

    Returns:
        The combined module or package
    """
    # Check if we're already inside this function in the current thread
    # This prevents `shim` calls in modules from triggering recursion loops for
    # auto-shimming modules
    if getattr(_shim_state, "active", False):
        # We're already running this function, so skip
        return None

    try:
        # Mark that we're now running this function
        _shim_state.active = True  # Validate module names

        if not lower:
            raise ValueError("Lower module name cannot be empty")

        # Use calling package name if 'upper' parameter name is empty
        if not upper:
            import inspect

            # Get the caller's frame to find its module
            frame = inspect.currentframe()
            if frame is not None:
                upper = frame.f_globals.get("__package__", "")
                if not upper:
                    upper = frame.f_globals.get("__name__", "")
                    if upper == "__main__":
                        raise ValueError("Cannot determine package name from __main__")
            if not upper:
                raise ValueError("Upper module name cannot be determined")

        # If mount not specified, use the upper module name
        if not mount and upper:
            mount = upper

        if not upper:
            raise ValueError("Upper module name cannot be empty")
        if not lower:
            raise ValueError("Lower module name cannot be empty")
        if not mount:
            raise ValueError("Mount point cannot be empty")

        # Register our finder in sys.meta_path if not already there
        if not any(isinstance(finder, ModShimFinder) for finder in sys.meta_path):
            sys.meta_path.insert(0, ModShimFinder())

        # Register the mapping for this mount point
        ModShimFinder.register_mapping(mount, upper, lower)

        # Re-import the mounted module if it has already been imported
        # This fixes issues when modules are mounted over their uppers
        if mount in sys.modules:
            del sys.modules[mount]
            _ = import_module(mount)

    finally:
        # Always clear the running flag when we exit
        _shim_state.active = False
