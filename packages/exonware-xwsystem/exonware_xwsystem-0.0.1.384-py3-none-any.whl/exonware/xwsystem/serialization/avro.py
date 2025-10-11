#exonware\xsystem\serialization\avro.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.384
Generation Date: September 04, 2025

Enhanced Apache Avro serialization with security, validation and performance optimizations.
"""

import io
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import fastavro - lazy installation system will handle it if enabled
import fastavro

from .base import ASerialization
from .errors import AvroError
from ..config.logging_setup import get_logger

logger = get_logger("xsystem.serialization.avro")

class AvroSerializer(ASerialization):
    """
    Enhanced Apache Avro serializer with schema validation and XSystem integration.
    
    Features:
    - Rich data structures
    - A compact, fast, binary data format
    - A container file, to store persistent data
    - Remote procedure call (RPC)
    - Simple integration with dynamic languages
    
    🚨 PRODUCTION LIBRARY: Uses fastavro - a fast, C-based implementation
    """

    def __init__(
        self,
        schema: Optional[Dict[str, Any]] = None,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 100.0,
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """
        Initialize Avro serializer with optional schema.

        Args:
            schema: Avro schema dictionary (required for serialization)
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation
        """
        # fastavro is automatically installed by xwimport if needed
        
        super().__init__(
            validate_input=validate_input,
            max_depth=max_depth,
            max_size_mb=max_size_mb,
            use_atomic_writes=use_atomic_writes,
            validate_paths=validate_paths,
            base_path=base_path,
        )
        self.schema = schema
        
        # Initialize configuration
        self._config = {}
        self._config.update({
            'schema': schema,
        })

    @property
    def format_name(self) -> str:
        """Get the serialization format name."""
        return "AVRO"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return ['.avro']

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/avro"

    @property
    def is_binary_format(self) -> bool:
        """Whether this is a binary format."""
        return True

    @property
    def supports_streaming(self) -> bool:
        """Whether streaming is supported."""
        return True

    def _validate_schema(self) -> None:
        """Validate schema using fastavro."""
        if not self.schema:
            raise AvroError("Schema is required for Avro serialization")
        try:
            fastavro.parse_schema(self.schema)
        except Exception as e:
            raise AvroError(f"Invalid Avro schema: {e}", e)

    def dumps(self, data: Any) -> str:
        """Serialize data to Avro base64 string."""
        try:
            if self.validate_input and self._data_validator:
                self._data_validator.validate_data_structure(data)
            self._validate_schema()
            import base64
            return base64.b64encode(self.dumps_binary(data)).decode('ascii')
        except Exception as e:
            raise AvroError(f"Serialization failed: {e}", e)

    def loads(self, data: Union[bytes, str]) -> Any:
        """Deserialize Avro data."""
        try:
            if isinstance(data, str):
                import base64
                data = base64.b64decode(data.encode('ascii'))
            return self.loads_bytes(data)
        except Exception as e:
            raise AvroError(f"Deserialization failed: {e}", e)

    def dumps_binary(self, data: Any) -> bytes:
        """Serialize data to Avro bytes."""
        try:
            if self.validate_input and self._data_validator:
                self._data_validator.validate_data_structure(data)
            self._validate_schema()
            
            # Ensure data is iterable for fastavro
            records = [data] if isinstance(data, dict) else data if isinstance(data, list) else [{"value": data}]
            
            import io
            bytes_io = io.BytesIO()
            fastavro.writer(bytes_io, self.schema, records)
            return bytes_io.getvalue()
        except Exception as e:
            raise AvroError(f"Binary serialization failed: {e}", e)

    def loads_bytes(self, data: bytes) -> Any:
        """Deserialize Avro bytes to Python object."""
        try:
            # Validate schema is loaded
            self._validate_schema()
            
            # Use fastavro for deserialization
            import io
            from fastavro import schemaless_reader
            
            bytes_reader = io.BytesIO(data)
            return schemaless_reader(bytes_reader, self.schema)
            
        except Exception as e:
            raise AvroError(f"Binary deserialization failed: {e}", e)

    def dumps_text(self, data: Any) -> str:
        """Not supported for binary formats."""
        raise AvroError("Avro is a binary format and does not support text-based serialization.", "AVRO")

    def loads_text(self, data: str) -> Any:
        """Not supported for binary formats."""
        raise AvroError("Avro is a binary format and does not support text-based serialization.", "AVRO")


# Convenience functions for common use cases
def dumps(data: Any, schema: Optional[Dict[str, Any]] = None, **kwargs: Any) -> str:
    """Serialize data to Avro base64-encoded string with default settings."""
    serializer = AvroSerializer(schema=schema, **kwargs)
    return serializer.dumps(data)


def loads(s: str, **kwargs: Any) -> Any:
    """Deserialize Avro string with default settings.""" 
    serializer = AvroSerializer(**kwargs)
    return serializer.loads(s)


def dumps_bytes(data: Any, schema: Optional[Dict[str, Any]] = None, **kwargs: Any) -> bytes:
    """Serialize data to Avro bytes with default settings."""
    serializer = AvroSerializer(schema=schema, **kwargs)
    return serializer.dumps_binary(data)


def loads_bytes(data: bytes, **kwargs: Any) -> Any:
    """Deserialize Avro bytes with default settings."""
    serializer = AvroSerializer(**kwargs)
    return serializer.loads_bytes(data)


def load_file(file_path: Union[str, Path], **kwargs: Any) -> Any:
    """Load Avro from file with default settings."""
    serializer = AvroSerializer(**kwargs)
    return serializer.load_file(file_path)


def save_file(data: Any, file_path: Union[str, Path], schema: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
    """Save data to Avro file with default settings."""
    serializer = AvroSerializer(schema=schema, **kwargs)
    return serializer.save_file(data, file_path)
