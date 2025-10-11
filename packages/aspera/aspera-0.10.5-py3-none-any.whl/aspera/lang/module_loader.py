"""
ASPERA Module Loader
====================
Import system for modular ASPERA programs.

Supports:
- File-based imports: import "path/to/module.aspera"
- Relative imports: import "./common.aspera"
- Named imports: import concepts from "./concepts.aspera"
- Circular dependency detection
- Module caching

Author: Christian Quintino De Luca - RTH Italia
Version: 0.1.0
"""

import os
from typing import Any, Dict, List, Optional, Set
from pathlib import Path
import hashlib
from copy import deepcopy


class CircularDependencyError(Exception):
    """Raised when circular dependency detected"""
    pass


class ModuleNotFoundError(Exception):
    """Raised when module file not found"""
    pass


class ImportResolver:
    """
    Resolves and loads ASPERA modules with import support.
    
    Features:
    - Dependency resolution
    - Circular dependency detection
    - Module caching
    - Relative path resolution
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize resolver.
        
        Args:
            base_dir: Base directory for resolving relative imports
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.module_cache: Dict[str, Dict[str, Any]] = {}
        self.loading_stack: List[str] = []
        self.dependency_graph: Dict[str, Set[str]] = {}
    
    def resolve_import(self, import_path: str, current_file: Optional[str] = None) -> str:
        """
        Resolve import path to absolute file path.
        
        Args:
            import_path: Import path (e.g., "./common.aspera", "lib/utils.aspera")
            current_file: Currently loading file (for relative imports)
        
        Returns:
            Absolute file path
        
        Raises:
            ModuleNotFoundError: If file doesn't exist
        """
        # Handle relative imports
        if import_path.startswith("./") or import_path.startswith("../"):
            if current_file:
                current_dir = Path(current_file).parent
                resolved = (current_dir / import_path).resolve()
            else:
                resolved = (self.base_dir / import_path).resolve()
        else:
            # Absolute from base_dir
            resolved = (self.base_dir / import_path).resolve()
        
        # Ensure .aspera extension
        if not str(resolved).endswith(".aspera"):
            resolved = Path(str(resolved) + ".aspera")
        
        if not resolved.exists():
            raise ModuleNotFoundError(f"Module not found: {import_path} (resolved to {resolved})")
        
        return str(resolved)
    
    def load_module(self, file_path: str) -> Dict[str, Any]:
        """
        Load ASPERA module and resolve all imports.
        
        Args:
            file_path: Path to .aspera file
        
        Returns:
            Merged AST with all imports resolved
        
        Raises:
            CircularDependencyError: If circular dependency detected
            ModuleNotFoundError: If imported module not found
        """
        abs_path = str(Path(file_path).resolve())
        
        # Check cache
        if abs_path in self.module_cache:
            return deepcopy(self.module_cache[abs_path])
        
        # Check for circular dependency
        if abs_path in self.loading_stack:
            cycle = " -> ".join(self.loading_stack + [abs_path])
            raise CircularDependencyError(f"Circular dependency detected: {cycle}")
        
        # Mark as loading
        self.loading_stack.append(abs_path)
        
        try:
            # Parse the file (support macros before parsing)
            from aspera.lang.parser import parse_aspera_with_macros
            
            with open(abs_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            ast = parse_aspera_with_macros(source)
            
            # Extract import statements
            imports = self._extract_imports(source, abs_path)
            
            # Record dependencies
            self.dependency_graph[abs_path] = set(imp["resolved_path"] for imp in imports)
            
            # Load and merge imported modules
            merged_ast = self._merge_imports(ast, imports)
            
            # Cache the result
            self.module_cache[abs_path] = merged_ast
            
            return deepcopy(merged_ast)
        
        finally:
            # Remove from loading stack
            self.loading_stack.pop()
    
    def _extract_imports(self, source: str, current_file: str) -> List[Dict[str, Any]]:
        """
        Extract import statements from source code.
        
        Args:
            source: ASPERA source code
            current_file: Current file path
        
        Returns:
            List of import dictionaries
        """
        imports = []
        
        for line_num, line in enumerate(source.split('\n'), 1):
            line = line.strip()
            
            # Simple import: import "path/to/file.aspera"
            if line.startswith('import ') and '"' in line:
                # Extract path
                start = line.index('"') + 1
                end = line.index('"', start)
                import_path = line[start:end]
                
                # Check for named imports: import concepts from "path"
                if ' from ' in line:
                    parts = line.split(' from ')
                    names = parts[0].replace('import', '').strip().split(',')
                    names = [n.strip() for n in names]
                else:
                    names = None  # Import all
                
                resolved = self.resolve_import(import_path, current_file)
                
                imports.append({
                    "line": line_num,
                    "path": import_path,
                    "resolved_path": resolved,
                    "names": names
                })
        
        return imports
    
    def _merge_imports(self, base_ast: Dict[str, Any], imports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge imported modules into base AST.
        
        Args:
            base_ast: Base AST to merge into
            imports: List of import specifications
        
        Returns:
            Merged AST
        """
        merged = deepcopy(base_ast)
        
        for imp in imports:
            # Load imported module
            imported_ast = self.load_module(imp["resolved_path"])
            
            # Filter nodes if named import
            if imp["names"]:
                imported_nodes = self._filter_nodes(imported_ast.get("nodes", []), imp["names"])
            else:
                imported_nodes = imported_ast.get("nodes", [])
            
            # Prepend imported nodes (imports come first)
            merged["nodes"] = imported_nodes + merged.get("nodes", [])
        
        return merged
    
    def _filter_nodes(self, nodes: List[Dict[str, Any]], names: List[str]) -> List[Dict[str, Any]]:
        """
        Filter nodes by name for selective imports.
        
        Args:
            nodes: List of AST nodes
            names: Names to import
        
        Returns:
            Filtered nodes
        """
        filtered = []
        for node in nodes:
            node_name = node.get("name", "")
            if node_name in names:
                filtered.append(node)
        
        return filtered
    
    def get_dependency_order(self, file_path: str) -> List[str]:
        """
        Get topologically sorted dependency order.
        
        Args:
            file_path: Root file path
        
        Returns:
            List of file paths in dependency order
        """
        # Load to build dependency graph
        self.load_module(file_path)
        
        # Topological sort
        visited = set()
        order = []
        
        def visit(path: str):
            if path in visited:
                return
            visited.add(path)
            
            for dep in self.dependency_graph.get(path, []):
                visit(dep)
            
            order.append(path)
        
        visit(str(Path(file_path).resolve()))
        
        return order
    
    def clear_cache(self):
        """Clear module cache"""
        self.module_cache.clear()
        self.loading_stack.clear()
        self.dependency_graph.clear()
    
    def get_module_hash(self, file_path: str) -> str:
        """
        Get hash of module for cache invalidation.
        
        Args:
            file_path: Module file path
        
        Returns:
            SHA256 hash of file content
        """
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()


# Global resolver instance
_global_resolver: Optional[ImportResolver] = None


def get_resolver(base_dir: Optional[str] = None) -> ImportResolver:
    """Get or create global import resolver"""
    global _global_resolver
    if _global_resolver is None or base_dir is not None:
        _global_resolver = ImportResolver(base_dir)
    return _global_resolver


def load_module_with_imports(file_path: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to load module with imports.
    
    Args:
        file_path: Path to .aspera file
        base_dir: Base directory for resolving imports
    
    Returns:
        Merged AST with all imports resolved
    
    Example:
        >>> ast = load_module_with_imports("myagent.aspera")
        >>> # All imports are automatically resolved and merged
    """
    resolver = get_resolver(base_dir)
    return resolver.load_module(file_path)

