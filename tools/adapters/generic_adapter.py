import re
from typing import List, Dict, Any
from .base_adapter import BaseAdapter

class GenericAdapter(BaseAdapter):
    """
    A generic adapter that uses Regex and string matching to detect violations.
    It can be used as a fallback for any language or for simple text-based checks.
    """

    # Default "rough" patterns for common prohibited operations
    # These can be overridden by contract definitions if needed
    DEFAULT_PATTERNS = {
        "dynamic_allocation": [r"\bmalloc\b", r"\bfree\b", r"\bnew\s+", r"\bdelete\b"],
        "filesystem_write":   [r"\bfopen\b", r"\bopen\s*\(", r"\bwrite\s*\(", r"\bpathlib\b"],
        "network_access":     [r"\bsocket\b", r"\brequests\.", r"\burllib\b", r"\bcurl\b", r"\bwget\b"],
        "logging_content":    [r"\bprintStackTrace\b", r"\bconsole\.trace\b", r"\bprint\s*\("]
    }

    def _check_pattern(self, filepath: str, patterns: List[str]) -> List[Dict[str, Any]]:
        violations = []
        try:
            with open(filepath, 'r', errors='ignore') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                for pattern in patterns:
                    if re.search(pattern, line):
                        violations.append({
                            "line": i + 1,
                            "message": f"Potential violation detected: pattern '{pattern}' found.",
                            "severity": "WARNING" # Generic checks are usually warnings/needs review
                        })
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
        
        return violations

    def check_resource_policy(self, filepath: str, policy: Dict[str, Any]) -> List[Dict[str, Any]]:
        category = policy.get("category")
        patterns = policy.get("forbidden_patterns", [])
        
        if not patterns:
            patterns = self.DEFAULT_PATTERNS.get(category, [])
            
        if not patterns:
            return []

        return self._check_pattern(filepath, patterns)

    def check_side_effect_policy(self, filepath: str, policy: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Logic matches resource policy for Generic Adapter (both use regex)
        return self.check_resource_policy(filepath, policy)
