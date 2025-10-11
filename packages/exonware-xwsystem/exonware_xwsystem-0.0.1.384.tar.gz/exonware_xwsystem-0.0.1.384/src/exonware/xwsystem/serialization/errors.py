#exonware/xwsystem/serialization/errors.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.384
Generation Date: September 04, 2025

Error classes for XWSystem serialization module.
"""

from typing import Optional


class SerializationError(Exception):
    """Base exception for serialization errors."""
    
    def __init__(self, message: str, format_name: str = "", original_error: Optional[Exception] = None):
        super().__init__(message)
        self.format_name = format_name
        self.original_error = original_error


class FormatDetectionError(SerializationError):
    """Error when format detection fails."""
    pass


class ValidationError(SerializationError):
    """Error when validation fails."""
    pass


class CsvError(Exception):
    """CSV serialization error."""
    pass


class CborError(Exception):
    """CBOR serialization error."""
    pass


class JsonError(SerializationError):
    """JSON-specific serialization error."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "JSON", original_error)


class YamlError(SerializationError):
    """YAML serialization error."""
    pass


class FormDataError(Exception):
    """Form data serialization error."""
    pass


class MultipartError(Exception):
    """Multipart serialization error."""
    pass


class MarshalError(Exception):
    """Marshal serialization error."""
    pass


class XmlError(Exception):
    """XML serialization error."""
    pass


class PickleError(Exception):
    """Pickle serialization error."""
    pass


class FlatBuffersError(SerializationError):
    """FlatBuffers serialization error."""
    pass


class CapnProtoError(SerializationError):
    """Cap'n Proto serialization error."""
    pass


class OrcError(SerializationError):
    """Apache ORC serialization error."""
    pass


class ParquetError(SerializationError):
    """Apache Parquet serialization error."""
    pass


class BsonError(SerializationError):
    """BSON serialization error."""
    pass


class ThriftError(SerializationError):
    """Apache Thrift serialization error."""
    pass


class ProtobufError(SerializationError):
    """Protocol Buffers serialization error."""
    pass


class AvroError(SerializationError):
    """Apache Avro serialization error."""
    pass


class Sqlite3Error(SerializationError):
    """SQLite3 serialization error."""
    pass


class ShelveError(SerializationError):
    """Shelve serialization error."""
    pass


class DbmError(SerializationError):
    """DBM serialization error."""
    pass


class ConfigParserError(SerializationError):
    """ConfigParser serialization error."""
    pass


class PlistlibError(SerializationError):
    """Plistlib serialization error."""
    pass


class TomlError(SerializationError):
    """TOML serialization error."""
    pass
