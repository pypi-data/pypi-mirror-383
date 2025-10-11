#exonware/xsystem/validation/base.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.385
Generation Date: September 04, 2025

Validation module base classes - abstract classes for validation functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable, Type, TypeVar
from .contracts import ValidationType, ValidationLevel, ConstraintType, SchemaType

T = TypeVar('T')


class AValidatorBase(ABC, Generic[T]):
    """Abstract base class for validation operations."""
    
    def __init__(self, validation_type: ValidationType = ValidationType.GENERIC):
        """
        Initialize validator.
        
        Args:
            validation_type: Type of validation
        """
        self.validation_type = validation_type
        self._validation_rules: Dict[str, Callable] = {}
        self._validation_errors: List[str] = []
        self._validation_level: ValidationLevel = ValidationLevel.BASIC
    
    @abstractmethod
    def validate(self, data: T) -> bool:
        """Validate data."""
        pass
    
    @abstractmethod
    def add_validation_rule(self, rule_name: str, rule_func: Callable[[T], bool]) -> None:
        """Add validation rule."""
        pass
    
    @abstractmethod
    def remove_validation_rule(self, rule_name: str) -> None:
        """Remove validation rule."""
        pass
    
    @abstractmethod
    def get_validation_errors(self) -> List[str]:
        """Get validation errors."""
        pass
    
    @abstractmethod
    def clear_validation_errors(self) -> None:
        """Clear validation errors."""
        pass
    
    @abstractmethod
    def set_validation_level(self, level: ValidationLevel) -> None:
        """Set validation level."""
        pass
    
    @abstractmethod
    def get_validation_level(self) -> ValidationLevel:
        """Get validation level."""
        pass
    
    @abstractmethod
    def get_validation_rules(self) -> List[str]:
        """Get validation rules."""
        pass
    
    @abstractmethod
    def is_valid(self, data: T) -> bool:
        """Check if data is valid."""
        pass


class ADataValidatorBase(ABC):
    """Abstract base class for data validation."""
    
    def __init__(self):
        """Initialize data validator."""
        self._validators: Dict[Type, AValidatorBase] = {}
        self._custom_validators: Dict[str, Callable] = {}
        self._validation_cache: Dict[str, bool] = {}
    
    @abstractmethod
    def validate_data(self, data: Any, data_type: Optional[Type] = None) -> bool:
        """Validate data."""
        pass
    
    @abstractmethod
    def validate_type(self, data: Any, expected_type: Type) -> bool:
        """Validate data type."""
        pass
    
    @abstractmethod
    def validate_value(self, data: Any, constraints: Dict[str, Any]) -> bool:
        """Validate data value against constraints."""
        pass
    
    @abstractmethod
    def validate_range(self, data: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                      max_value: Optional[Union[int, float]] = None) -> bool:
        """Validate data range."""
        pass
    
    @abstractmethod
    def validate_length(self, data: Union[str, List, Dict], min_length: Optional[int] = None, 
                       max_length: Optional[int] = None) -> bool:
        """Validate data length."""
        pass
    
    @abstractmethod
    def validate_pattern(self, data: str, pattern: str) -> bool:
        """Validate data pattern."""
        pass
    
    @abstractmethod
    def validate_enum(self, data: Any, enum_values: List[Any]) -> bool:
        """Validate data against enum values."""
        pass
    
    @abstractmethod
    def validate_required(self, data: Any) -> bool:
        """Validate required data."""
        pass
    
    @abstractmethod
    def validate_optional(self, data: Any) -> bool:
        """Validate optional data."""
        pass
    
    @abstractmethod
    def register_validator(self, data_type: Type, validator: AValidatorBase) -> None:
        """Register validator for data type."""
        pass
    
    @abstractmethod
    def unregister_validator(self, data_type: Type) -> None:
        """Unregister validator for data type."""
        pass
    
    @abstractmethod
    def get_validator(self, data_type: Type) -> Optional[AValidatorBase]:
        """Get validator for data type."""
        pass


class ATypeSafetyBase(ABC):
    """Abstract base class for type safety operations."""
    
    def __init__(self):
        """Initialize type safety."""
        self._type_annotations: Dict[str, Type] = {}
        self._type_checks: Dict[str, bool] = {}
        self._strict_mode = False
    
    @abstractmethod
    def check_type(self, data: Any, expected_type: Type) -> bool:
        """Check data type."""
        pass
    
    @abstractmethod
    def check_types(self, data: Dict[str, Any], type_annotations: Dict[str, Type]) -> bool:
        """Check multiple data types."""
        pass
    
    @abstractmethod
    def coerce_type(self, data: Any, target_type: Type) -> Any:
        """Coerce data to target type."""
        pass
    
    @abstractmethod
    def is_type_safe(self, data: Any, expected_type: Type) -> bool:
        """Check if data is type safe."""
        pass
    
    @abstractmethod
    def get_type_info(self, data: Any) -> Dict[str, Any]:
        """Get type information."""
        pass
    
    @abstractmethod
    def validate_type_annotations(self, annotations: Dict[str, Type]) -> bool:
        """Validate type annotations."""
        pass
    
    @abstractmethod
    def set_strict_mode(self, strict: bool) -> None:
        """Set strict type checking mode."""
        pass
    
    @abstractmethod
    def is_strict_mode(self) -> bool:
        """Check if strict mode is enabled."""
        pass
    
    @abstractmethod
    def get_type_errors(self) -> List[str]:
        """Get type errors."""
        pass
    
    @abstractmethod
    def clear_type_errors(self) -> None:
        """Clear type errors."""
        pass


class ADeclarativeValidatorBase(ABC):
    """Abstract base class for declarative validation."""
    
    def __init__(self):
        """Initialize declarative validator."""
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._schema_validators: Dict[str, Callable] = {}
        self._validation_results: Dict[str, Dict[str, Any]] = {}
    
    @abstractmethod
    def define_schema(self, schema_name: str, schema_definition: Dict[str, Any]) -> None:
        """Define validation schema."""
        pass
    
    @abstractmethod
    def validate_against_schema(self, data: Any, schema_name: str) -> bool:
        """Validate data against schema."""
        pass
    
    @abstractmethod
    def get_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Get schema definition."""
        pass
    
    @abstractmethod
    def list_schemas(self) -> List[str]:
        """List all schemas."""
        pass
    
    @abstractmethod
    def remove_schema(self, schema_name: str) -> bool:
        """Remove schema."""
        pass
    
    @abstractmethod
    def validate_schema_definition(self, schema_definition: Dict[str, Any]) -> bool:
        """Validate schema definition."""
        pass
    
    @abstractmethod
    def get_validation_result(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Get validation result."""
        pass
    
    @abstractmethod
    def get_validation_errors(self, schema_name: str) -> List[str]:
        """Get validation errors for schema."""
        pass
    
    @abstractmethod
    def clear_validation_results(self) -> None:
        """Clear validation results."""
        pass
    
    @abstractmethod
    def export_schema(self, schema_name: str, format: str = "json") -> str:
        """Export schema."""
        pass
    
    @abstractmethod
    def import_schema(self, schema_name: str, schema_data: str, format: str = "json") -> None:
        """Import schema."""
        pass


class AConstraintValidatorBase(ABC):
    """Abstract base class for constraint validation."""
    
    def __init__(self):
        """Initialize constraint validator."""
        self._constraints: Dict[str, Dict[str, Any]] = {}
        self._constraint_validators: Dict[ConstraintType, Callable] = {}
        self._constraint_results: Dict[str, bool] = {}
    
    @abstractmethod
    def add_constraint(self, constraint_name: str, constraint_type: ConstraintType, 
                      constraint_value: Any) -> None:
        """Add constraint."""
        pass
    
    @abstractmethod
    def remove_constraint(self, constraint_name: str) -> None:
        """Remove constraint."""
        pass
    
    @abstractmethod
    def validate_constraint(self, data: Any, constraint_name: str) -> bool:
        """Validate data against constraint."""
        pass
    
    @abstractmethod
    def validate_all_constraints(self, data: Any) -> Dict[str, bool]:
        """Validate data against all constraints."""
        pass
    
    @abstractmethod
    def get_constraint(self, constraint_name: str) -> Optional[Dict[str, Any]]:
        """Get constraint definition."""
        pass
    
    @abstractmethod
    def list_constraints(self) -> List[str]:
        """List all constraints."""
        pass
    
    @abstractmethod
    def get_constraint_type(self, constraint_name: str) -> Optional[ConstraintType]:
        """Get constraint type."""
        pass
    
    @abstractmethod
    def get_constraint_value(self, constraint_name: str) -> Any:
        """Get constraint value."""
        pass
    
    @abstractmethod
    def clear_constraints(self) -> None:
        """Clear all constraints."""
        pass
    
    @abstractmethod
    def get_constraint_results(self) -> Dict[str, bool]:
        """Get constraint validation results."""
        pass
    
    @abstractmethod
    def get_failed_constraints(self) -> List[str]:
        """Get failed constraints."""
        pass
    
    @abstractmethod
    def get_passed_constraints(self) -> List[str]:
        """Get passed constraints."""
        pass
