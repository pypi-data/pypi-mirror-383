"""Adapter Pattern detector."""

import ast
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Set

from vera_syntaxis.pattern_detectors.base import BasePatternDetector, PatternOpportunity

logger = logging.getLogger(__name__)


@dataclass
class TranslationMethod:
    """Information about a translation method."""
    file_path: Path
    method_name: str
    line_number: int
    field_mappings: int
    has_external_call: bool


@dataclass
class InterfaceClass:
    """Information about a class implementing similar interface."""
    name: str
    file_path: Path
    line_number: int
    methods: Set[str]


class AdapterDetector(BasePatternDetector):
    """Detects opportunities for Adapter pattern."""
    
    @property
    def pattern_name(self) -> str:
        return "Adapter"
    
    @property
    def pattern_description(self) -> str:
        return "Convert incompatible interfaces to work together"
    
    def detect(self) -> List[PatternOpportunity]:
        """Detect Adapter pattern opportunities."""
        logger.debug("Running Adapter pattern detection")
        
        opportunities = []
        
        # Strategy 1: Find translation methods
        translations = self._find_translation_methods()
        for trans in translations:
            if trans.field_mappings >= 3:
                confidence = 0.85 if trans.has_external_call else 0.65
                opportunity = self._create_adapter_from_translation(trans, confidence)
                opportunities.append(opportunity)
        
        # Strategy 2: Find similar interfaces
        interface_groups = self._find_similar_interfaces()
        for group_name, classes in interface_groups.items():
            if len(classes) >= 2:
                confidence = 0.9 if len(classes) >= 3 else 0.7
                opportunity = self._create_adapter_from_interfaces(
                    group_name, classes, confidence
                )
                opportunities.append(opportunity)
        
        self.opportunities = opportunities
        return opportunities
    
    def _find_translation_methods(self) -> List[TranslationMethod]:
        """Find methods that translate data structures."""
        translations = []
        
        for file_path, parsed_file in self.context.parsed_files.items():
            for node in ast.walk(parsed_file.ast_root):
                if isinstance(node, ast.FunctionDef):
                    # Look for dictionary/object field mapping
                    field_mappings = self._count_field_mappings(node)
                    has_external_call = self._has_external_api_call(node)
                    
                    if field_mappings >= 2:
                        translations.append(TranslationMethod(
                            file_path=file_path,
                            method_name=node.name,
                            line_number=node.lineno,
                            field_mappings=field_mappings,
                            has_external_call=has_external_call
                        ))
        
        return translations
    
    def _count_field_mappings(self, func_node: ast.FunctionDef) -> int:
        """Count dictionary key mappings in function."""
        mappings = 0
        
        for node in ast.walk(func_node):
            # Look for dictionary creation with field mapping
            if isinstance(node, ast.Dict):
                # Count key-value pairs that look like field mappings
                for key, value in zip(node.keys, node.values):
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        # Check if value accesses another dict/object
                        if isinstance(value, ast.Subscript) or isinstance(value, ast.Attribute):
                            mappings += 1
        
        return mappings
    
    def _has_external_api_call(self, func_node: ast.FunctionDef) -> bool:
        """Check if function calls external API."""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # Check for method calls that might be external APIs
                    attr_name = node.func.attr
                    if any(keyword in attr_name.lower() 
                           for keyword in ['request', 'get', 'post', 'fetch', 'api', 'call']):
                        return True
            if isinstance(node, ast.Return):
                # Check if returning call result
                if isinstance(node.value, ast.Call):
                    return True
        
        return False
    
    def _find_similar_interfaces(self) -> Dict[str, List[InterfaceClass]]:
        """Find classes with similar method signatures."""
        classes_by_methods = defaultdict(list)
        
        for file_path, parsed_file in self.context.parsed_files.items():
            for node in ast.walk(parsed_file.ast_root):
                if isinstance(node, ast.ClassDef):
                    # Get public methods
                    methods = set()
                    for class_node in node.body:
                        if isinstance(class_node, ast.FunctionDef):
                            if not class_node.name.startswith('_') or class_node.name == '__init__':
                                methods.add(class_node.name)
                    
                    if methods:
                        # Use frozenset of methods as key to group similar classes
                        method_signature = frozenset(methods)
                        classes_by_methods[method_signature].append(
                            InterfaceClass(
                                name=node.name,
                                file_path=file_path,
                                line_number=node.lineno,
                                methods=methods
                            )
                        )
        
        # Filter to groups with multiple classes
        groups = {}
        for methods, classes in classes_by_methods.items():
            if len(classes) >= 2:
                # Create group name from common method names
                common_methods = list(methods)[:2]
                group_name = f"Interface with {', '.join(common_methods)}"
                groups[group_name] = classes
        
        return groups
    
    def _create_adapter_from_translation(
        self,
        trans: TranslationMethod,
        confidence: float
    ) -> PatternOpportunity:
        """Create opportunity from translation method."""
        description = (
            f"Method '{trans.method_name}' performs {trans.field_mappings} field mappings. "
            f"Consider Adapter pattern for interface translation"
        )
        
        benefit = (
            "Separates interface conversion logic, enables reuse, "
            "makes integration with third-party code cleaner"
        )
        
        example = f"""# Before: Translation scattered in code
# def {trans.method_name}(data):
#     legacy_format = {{'old_id': data['id'], 'old_name': data['name']}}
#     return external_api.process(legacy_format)

# After: Adapter pattern
class ModernToLegacyAdapter:
    def __init__(self, legacy_system):
        self.legacy_system = legacy_system
    
    def process(self, modern_data):
        # Translate interface
        legacy_data = self._translate(modern_data)
        return self.legacy_system.process(legacy_data)
    
    def _translate(self, modern_data):
        return {{
            'old_id': modern_data['id'],
            'old_name': modern_data['name']
        }}
"""
        
        return self._create_opportunity(
            file_path=trans.file_path,
            line_number=trans.line_number,
            confidence=confidence,
            description=description,
            trigger_type="Field Mapping Translation",
            benefit=benefit,
            example_code=example,
            evidence={
                'method_name': trans.method_name,
                'field_mappings': trans.field_mappings,
                'has_external_call': trans.has_external_call
            }
        )
    
    def _create_adapter_from_interfaces(
        self,
        group_name: str,
        classes: List[InterfaceClass],
        confidence: float
    ) -> PatternOpportunity:
        """Create opportunity from similar interfaces."""
        class_names = [c.name for c in classes]
        
        description = (
            f"Found {len(classes)} classes with similar interfaces: "
            f"{', '.join(class_names)}. Standardize with Adapter pattern"
        )
        
        benefit = (
            "Provides consistent interface, simplifies client code, "
            "enables swapping implementations"
        )
        
        example = f"""# Before: Different interfaces for same functionality
# class RequestsClient:
#     def fetch(self, url): ...
# class URLlibClient:
#     def get(self, url): ...

# After: Adapter pattern with common interface
class HTTPClientInterface(ABC):
    @abstractmethod
    def fetch(self, url: str) -> Response:
        pass

class RequestsAdapter(HTTPClientInterface):
    def __init__(self):
        self.client = requests.Session()
    
    def fetch(self, url: str) -> Response:
        return self.client.get(url)

class URLlibAdapter(HTTPClientInterface):
    def fetch(self, url: str) -> Response:
        return urllib.request.urlopen(url)

# Usage - client code uses common interface
client: HTTPClientInterface = RequestsAdapter()
response = client.fetch(url)
"""
        
        related_files = list(set(c.file_path for c in classes))
        
        return self._create_opportunity(
            file_path=classes[0].file_path,
            line_number=classes[0].line_number,
            confidence=confidence,
            description=description,
            trigger_type="Similar Interfaces",
            benefit=benefit,
            example_code=example,
            related_files=related_files,
            evidence={
                'class_count': len(classes),
                'classes': class_names,
                'group': group_name
            }
        )
