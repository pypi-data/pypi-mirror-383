#exonware\xsystem\serialization\cbor.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.386
Generation Date: September 04, 2025

CBOR (Concise Binary Object Representation) Serializer Implementation

Provides CBOR serialization with RFC 8949 compliance, binary format support,
and integration with XSystem utilities for security and validation.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import io
from pathlib import Path

from .contracts import ISerialization
from .base import ASerialization

# Import cbor2 - lazy installation system will handle it if missing
import cbor2


class CborSerializer(ASerialization):
    """
    CBOR (Concise Binary Object Representation) serializer.
    
    Features:
    - RFC 8949 compliant binary serialization
    - Compact binary representation
    - Support for diverse data types including datetime, decimal
    - Optional canonical encoding
    - Security validation
    - Atomic file operations
    """
    
    def __init__(
        self,
        canonical: bool = False,
        datetime_as_timestamp: bool = True,
        timezone_aware: bool = True,
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 100,
        max_size_mb: int = 50
    ) -> None:
        """
        Initialize CBOR serializer.
        
        Args:
            canonical: Use canonical encoding for reproducible output
            datetime_as_timestamp: Encode datetime as timestamps vs strings
            timezone_aware: Handle timezone-aware datetime objects
            validate_input: Enable input data validation
            validate_paths: Enable path security validation
            use_atomic_writes: Use atomic file operations
            max_depth: Maximum nesting depth for security
            max_size_mb: Maximum data size in MB
        """
        # Lazy installation system will handle cbor2 if missing
        
        super().__init__(
            validate_input=validate_input,
            validate_paths=validate_paths,
            use_atomic_writes=use_atomic_writes,
            max_depth=max_depth,
            max_size_mb=max_size_mb
        )
        
        self._canonical = canonical
        self._datetime_as_timestamp = datetime_as_timestamp
        self._timezone_aware = timezone_aware
    
    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "CBOR"
    
    @property
    def file_extensions(self) -> Tuple[str, ...]:
        """Get supported file extensions."""
        return (".cbor", ".cbr")
    
    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/cbor"
    
    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return True
    
    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True
    
    def dumps_binary(self, data: Any) -> bytes:
        """
        Serialize data to CBOR bytes.
        
        Args:
            data: Data to serialize
            
        Returns:
            CBOR bytes
            
        Raises:
            ValueError: If data validation fails
            TypeError: If data contains non-serializable types
        """
        if self.validate_input:
            self._validate_data_security(data)
        
        try:
            result = cbor2.dumps(
                data,
                canonical=self._canonical,
                datetime_as_timestamp=self._datetime_as_timestamp
            )
            
            return result
            
        except Exception as e:
            self._handle_serialization_error("serialization", e)
    
    def loads_bytes(self, data: bytes) -> Any:
        """
        Deserialize CBOR data.
        
        Args:
            data: CBOR bytes to deserialize
            
        Returns:
            Deserialized data
            
        Raises:
            ValueError: If data is invalid or validation fails
        """
        if isinstance(data, str):
            raise ValueError("CBOR data must be bytes, not string")
        
        if not isinstance(data, (bytes, bytearray)):
            raise ValueError(f"Expected bytes or bytearray, got {type(data)}")
        
        try:
            result = cbor2.loads(data)
            
            if self.validate_input:
                self._validate_data_security(result)
            
            return result
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)
    
    # 🎯 OPTIMIZATION: save_file and load_file inherited from base class!
    # Base class automatically handles binary format based on is_binary_format flag
    
    def stream_encode(self, data_stream) -> bytes:
        """
        Encode data from a stream to CBOR.
        
        Args:
            data_stream: Iterable of data objects to encode
            
        Returns:
            CBOR bytes
        """
        # Lazy install handles cbor2
        
        buffer = io.BytesIO()
        
        for item in data_stream:
            if self.validate_input:
                self._validate_data_security(item)
            
            encoded_item = cbor2.dumps(
                item,
                canonical=self._canonical,
                datetime_as_timestamp=self._datetime_as_timestamp
            )
            buffer.write(encoded_item)
        
        return buffer.getvalue()
    
    def stream_decode(self, data: bytes):
        """
        Decode CBOR data as a stream.
        
        Args:
            data: CBOR bytes to decode
            
        Yields:
            Decoded objects
        """
        # Lazy install handles cbor2
        
        fp = io.BytesIO(data)
        decoder = cbor2.CBORDecoder(fp)
        
        try:
            while True:
                try:
                    item = decoder.decode()
                    if self.validate_input:
                        self._validate_data_security(item)
                    yield item
                except cbor2.CBORDecodeError:
                    # End of stream
                    break
        except Exception as e:
            raise ValueError(f"CBOR stream decoding failed: {e}") from e
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get CBOR format schema information.
        
        Returns:
            Schema information dictionary
        """
        return {
            "format": "CBOR",
            "version": "RFC 8949",
            "description": "Concise Binary Object Representation",
            "features": {
                "binary": True,
                "canonical_encoding": self._canonical,
                "datetime_support": True,
                "streaming": True,
                "timezone_aware": self._timezone_aware
            },
            "supported_types": [
                "int", "float", "str", "bytes", "bool", "None",
                "list", "dict", "datetime", "decimal", "uuid"
            ],
            "file_extensions": list(self.file_extensions),
            "mime_type": self.mime_type
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current serializer configuration.
        
        Returns:
            Configuration dictionary
        """
        config = super().get_config()
        config.update({
            "canonical": self._canonical,
            "datetime_as_timestamp": self._datetime_as_timestamp,
            "timezone_aware": self._timezone_aware
        })
        return config


# Module-level convenience functions for consistent API
def dumps(data: Any, **kwargs: Any) -> str:
    """Serialize data to CBOR string (base64-encoded) with default settings."""
    serializer = CborSerializer(**kwargs)
    return serializer.dumps(data)


def loads(s: str, **kwargs: Any) -> Any:
    """Deserialize CBOR string with default settings."""
    serializer = CborSerializer(**kwargs)
    return serializer.loads(s)


def dumps_bytes(data: Any, **kwargs: Any) -> bytes:
    """Serialize data to CBOR bytes with default settings."""
    serializer = CborSerializer(**kwargs)
    return serializer.dumps_binary(data)


def loads_bytes(data: bytes, **kwargs: Any) -> Any:
    """Deserialize CBOR bytes with default settings."""
    serializer = CborSerializer(**kwargs)
    return serializer.loads_bytes(data)


def load_file(file_path: Union[str, Path], **kwargs: Any) -> Any:
    """Load CBOR from file with default settings."""
    serializer = CborSerializer(**kwargs)
    return serializer.load_file(file_path)


def save_file(data: Any, file_path: Union[str, Path], **kwargs: Any) -> None:
    """Save data to CBOR file with default settings."""
    serializer = CborSerializer(**kwargs)
    return serializer.save_file(data, file_path)


# Error classes for consistency with other serializers
class CborError(Exception):
    """Base exception for CBOR serialization errors."""
    pass
