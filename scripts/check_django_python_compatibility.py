#!/usr/bin/env python3
"""
Django 4.2 + Python 3.10+ Compatibility Checker

This script audits the codebase for known compatibility issues that can be
caught statically before runtime. Run this before commits to catch issues early.

Issues checked:
- collections.Iterable/Mapping/etc moved to collections.abc (Python 3.10+)
- ForeignKey missing on_delete parameter (required in Django 2.0+)
- GeoManager removed in Django 3.2+ (use Manager)
- Deprecated Django utility imports (ugettext, force_text, etc)
- django.conf.urls.url removed in Django 4.0+ (use django.urls.re_path)
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set

# Python 3.10+ incompatibilities: imports moved to collections.abc
COLLECTIONS_ABC_MOVED = {
    'Iterable', 'Iterator', 'Reversible', 'Generator',
    'Sized', 'Callable', 'Collection', 'Container',
    'Hashable', 'Mapping', 'MutableMapping', 'Sequence',
    'MutableSequence', 'Set', 'MutableSet'
}

# Django deprecated APIs
DEPRECATED_DJANGO_IMPORTS = {
    'django.utils.translation': {
        'ugettext', 'ugettext_lazy', 'ugettext_noop', 'ungettext',
        'ungettext_lazy'
    },
    'django.utils.encoding': {
        'smart_text', 'smart_str', 'force_text', 'force_bytes',
        'escape_uri_path'
    },
    'django.conf.urls': {'url'},
    'django.db.models.fields': {'FieldDoesNotExist'},
    'django.core': {'urlresolvers'},
}

# Known removed classes
REMOVED_CLASSES = {
    'GeoManager': 'Use models.Manager instead',
    'NullBooleanField': 'Use BooleanField(null=True) instead',
}


class CompatibilityChecker(ast.NodeVisitor):
    """AST visitor to find compatibility issues."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.issues: List[Tuple[int, str]] = []
        self.current_imports: Dict[str, str] = {}  # {name: module}
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Check import statements for deprecated imports."""
        if node.module is None:
            return
        
        # Check for collections.* imports that moved to collections.abc
        if node.module == 'collections':
            for alias in node.names:
                name = alias.name
                if name in COLLECTIONS_ABC_MOVED:
                    self.issues.append((
                        node.lineno,
                        f"Import '{name}' from collections moved to collections.abc (Python 3.10+). "
                        f"Change to: from collections.abc import {name}"
                    ))
                # Track for attribute access checking
                if name != '*':
                    self.current_imports[name] = 'collections'
        
        # Check for deprecated Django imports
        for deprecated_module, deprecated_names in DEPRECATED_DJANGO_IMPORTS.items():
            if node.module == deprecated_module:
                for alias in node.names:
                    name = alias.name
                    if name in deprecated_names:
                        replacement = self._get_replacement(deprecated_module, name)
                        self.issues.append((
                            node.lineno,
                            f"Deprecated import '{name}' from '{deprecated_module}'. {replacement}"
                        ))
                    if name != '*':
                        self.current_imports[name] = deprecated_module
        
        self.generic_visit(node)
    
    def visit_Attribute(self, node: ast.Attribute):
        """Check for uses of removed classes like GeoManager."""
        if node.attr in REMOVED_CLASSES:
            suggestion = REMOVED_CLASSES[node.attr]
            self.issues.append((
                node.lineno,
                f"'{node.attr}' was removed in Django 3.2+. {suggestion}"
            ))
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        """Check for ForeignKey without on_delete parameter."""
        # Check if this is a ForeignKey call
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'ForeignKey':
                # Check if on_delete is in kwargs
                has_on_delete = any(kw.arg == 'on_delete' for kw in node.keywords)
                if not has_on_delete:
                    self.issues.append((
                        node.lineno,
                        "ForeignKey missing 'on_delete' parameter (required in Django 2.0+). "
                        "Add: on_delete=models.CASCADE (or another deletion behavior)"
                    ))
        self.generic_visit(node)
    
    @staticmethod
    def _get_replacement(module: str, name: str) -> str:
        """Get replacement guidance for deprecated imports."""
        replacements = {
            ('django.utils.translation', 'ugettext'): 'Use gettext instead.',
            ('django.utils.translation', 'ugettext_lazy'): 'Use gettext_lazy instead.',
            ('django.utils.translation', 'ugettext_noop'): 'Use gettext_noop instead.',
            ('django.utils.encoding', 'smart_text'): 'Use force_str instead.',
            ('django.utils.encoding', 'smart_str'): 'Use force_str instead.',
            ('django.utils.encoding', 'force_text'): 'Use force_str instead.',
            ('django.conf.urls', 'url'): 'Use django.urls.re_path or django.urls.path instead.',
            ('django.db.models.fields', 'FieldDoesNotExist'): 'Import from django.core.exceptions instead.',
            ('django.core', 'urlresolvers'): 'Use django.urls instead.',
        }
        return replacements.get((module, name), 'Update to modern Django equivalent.')


def check_file(filepath: Path) -> List[Tuple[int, str]]:
    """Check a single Python file for compatibility issues."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(filepath))
        checker = CompatibilityChecker(str(filepath))
        checker.visit(tree)
        return checker.issues
    except SyntaxError as e:
        return [(e.lineno, f"Syntax Error: {e.msg}")]
    except Exception as e:
        return [(0, f"Error parsing file: {str(e)}")]


def main():
    """Check all Python files in opentreemap directory."""
    root = Path('opentreemap')
    
    if not root.exists():
        print(f"Error: {root} directory not found")
        print("Run this script from the repository root")
        sys.exit(1)
    
    all_issues: Dict[Path, List[Tuple[int, str]]] = {}
    
    # Find all Python files
    python_files = list(root.rglob('*.py'))
    print(f"Checking {len(python_files)} Python files...")
    
    for filepath in python_files:
        # Skip migrations and common non-problematic paths
        if 'migrations' in str(filepath) or '__pycache__' in str(filepath):
            continue
        
        issues = check_file(filepath)
        if issues:
            all_issues[filepath] = issues
    
    # Report findings
    if not all_issues:
        print("✅ No compatibility issues found!")
        return 0
    
    print(f"\n⚠️  Found {sum(len(i) for i in all_issues.values())} compatibility issue(s):\n")
    
    for filepath in sorted(all_issues.keys()):
        print(f"📄 {filepath}")
        for lineno, issue in all_issues[filepath]:
            print(f"   Line {lineno}: {issue}")
        print()
    
    return 1


if __name__ == '__main__':
    sys.exit(main())
