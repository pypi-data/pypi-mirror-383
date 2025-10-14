"""Micronaut API parser."""

import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from parsers.base import BaseParser
from core.models import (
    APIEndpoint,
    APIParameter,
    APIResponse,
    DiscoveryResult,
    FrameworkType,
    HTTPMethod,
    ParameterLocation,
)


class MicronautParser(BaseParser):
    """Parser for Micronaut REST APIs."""

    def parse(self) -> DiscoveryResult:
        """Parse Micronaut source files for API endpoints."""
        endpoints = []
        java_files = self.find_files("*.java")

        for java_file in java_files:
            content = self.read_file(java_file)
            if content and self._is_controller(content):
                endpoints.extend(self._parse_controller(java_file, content))

        return DiscoveryResult(
            framework=FrameworkType.MICRONAUT,
            endpoints=endpoints,
            title="Micronaut API",
        )

    def get_framework_type(self) -> FrameworkType:
        """Get the framework type."""
        return FrameworkType.MICRONAUT

    def _is_controller(self, content: str) -> bool:
        """Check if the class is a Micronaut controller."""
        return "@Controller" in content

    def _parse_controller(self, file_path: Path, content: str) -> List[APIEndpoint]:
        """Parse a controller file for endpoints."""
        endpoints = []
        
        # Extract class-level @Controller path
        class_path = self._extract_controller_path(content)
        
        # Find all HTTP method annotations
        methods = self._extract_methods(content)
        
        for method_info in methods:
            endpoint = self._create_endpoint(
                method_info,
                class_path,
                file_path,
            )
            if endpoint:
                endpoints.append(endpoint)

        return endpoints

    def _extract_controller_path(self, content: str) -> str:
        """Extract class-level @Controller path."""
        # Match @Controller("/path") or @Controller(value = "/path")
        patterns = [
            r'@Controller\s*\(\s*"([^"]+)"\s*\)',
            r'@Controller\s*\(\s*value\s*=\s*"([^"]+)"\s*\)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return ""

    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract method information from controller."""
        methods = []
        
        # Patterns for Micronaut HTTP annotations
        mapping_patterns = [
            (r'@Get\s*\(\s*"([^"]+)"\s*\)', HTTPMethod.GET),
            (r'@Get\s*\(\s*uri\s*=\s*"([^"]+)"\s*\)', HTTPMethod.GET),
            (r'@Post\s*\(\s*"([^"]+)"\s*\)', HTTPMethod.POST),
            (r'@Post\s*\(\s*uri\s*=\s*"([^"]+)"\s*\)', HTTPMethod.POST),
            (r'@Put\s*\(\s*"([^"]+)"\s*\)', HTTPMethod.PUT),
            (r'@Put\s*\(\s*uri\s*=\s*"([^"]+)"\s*\)', HTTPMethod.PUT),
            (r'@Delete\s*\(\s*"([^"]+)"\s*\)', HTTPMethod.DELETE),
            (r'@Delete\s*\(\s*uri\s*=\s*"([^"]+)"\s*\)', HTTPMethod.DELETE),
            (r'@Patch\s*\(\s*"([^"]+)"\s*\)', HTTPMethod.PATCH),
            (r'@Patch\s*\(\s*uri\s*=\s*"([^"]+)"\s*\)', HTTPMethod.PATCH),
        ]
        
        # Also handle methods without explicit URI (use method name)
        no_uri_patterns = [
            (r'@Get\s*\n', HTTPMethod.GET),
            (r'@Post\s*\n', HTTPMethod.POST),
            (r'@Put\s*\n', HTTPMethod.PUT),
            (r'@Delete\s*\n', HTTPMethod.DELETE),
            (r'@Patch\s*\n', HTTPMethod.PATCH),
        ]
        
        for pattern, http_method in mapping_patterns:
            for match in re.finditer(pattern, content):
                path = match.group(1)
                method_start = match.end()
                method_signature = self._extract_method_signature(content, method_start)
                
                methods.append({
                    "path": path,
                    "method": http_method,
                    "signature": method_signature,
                    "position": match.start(),
                })
        
        for pattern, http_method in no_uri_patterns:
            for match in re.finditer(pattern, content):
                method_start = match.end()
                method_signature = self._extract_method_signature(content, method_start)
                # Use method name as path
                method_name = self._extract_method_name(method_signature)
                path = f"/{method_name}" if method_name else ""
                
                if path:
                    methods.append({
                        "path": path,
                        "method": http_method,
                        "signature": method_signature,
                        "position": match.start(),
                    })
        
        return methods

    def _extract_method_signature(self, content: str, start_pos: int) -> str:
        """Extract Java method signature after annotation."""
        method_pattern = r'(public|private|protected)?\s+\w+\s+\w+\s*\([^)]*\)'
        match = re.search(method_pattern, content[start_pos:start_pos+500])
        if match:
            return match.group(0)
        return ""

    def _extract_method_name(self, signature: str) -> str:
        """Extract method name from signature."""
        match = re.search(r'\s+(\w+)\s*\(', signature)
        if match:
            return match.group(1)
        return ""

    def _create_endpoint(
        self,
        method_info: Dict[str, Any],
        class_path: str,
        file_path: Path,
    ) -> Optional[APIEndpoint]:
        """Create an APIEndpoint from method information."""
        # Combine class path and method path
        full_path = self._combine_paths(class_path, method_info["path"])
        full_path = self.normalize_path(full_path)
        
        # Extract parameters from signature
        parameters = self._extract_parameters(method_info["signature"], full_path)
        
        # Create endpoint
        endpoint = APIEndpoint(
            path=full_path,
            method=method_info["method"],
            operation_id=self._generate_operation_id(full_path, method_info["method"]),
            parameters=parameters,
            responses=[
                APIResponse(
                    status_code=200,
                    description="Successful response",
                )
            ],
            source_file=self.get_relative_path(file_path),
        )
        
        return endpoint

    def _combine_paths(self, base: str, path: str) -> str:
        """Combine base path and method path."""
        if not base:
            return path
        if not path:
            return base
        
        base = base.rstrip('/')
        path = path.lstrip('/')
        
        return f"{base}/{path}"

    def _extract_parameters(self, signature: str, path: str) -> List[APIParameter]:
        """Extract parameters from method signature."""
        parameters = []
        
        # Extract path parameters
        path_vars = self.extract_path_variables(path)
        for var in path_vars:
            parameters.append(
                APIParameter(
                    name=var,
                    location=ParameterLocation.PATH,
                    required=True,
                    type="string",
                )
            )
        
        # Extract query parameters from @QueryValue
        query_params = re.findall(r'@QueryValue[^)]*\s+\w+\s+(\w+)', signature)
        for param in query_params:
            if param not in path_vars:
                parameters.append(
                    APIParameter(
                        name=param,
                        location=ParameterLocation.QUERY,
                        required=False,
                        type="string",
                    )
                )
        
        return parameters

    def _generate_operation_id(self, path: str, method: HTTPMethod) -> str:
        """Generate operation ID from path and method."""
        path_parts = [p for p in path.split('/') if p and not p.startswith('{')]
        operation_id = method.value.lower() + ''.join(p.capitalize() for p in path_parts)
        return operation_id

