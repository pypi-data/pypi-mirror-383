"""
MIT License

Copyright (c) 2025 Saleem Ahmad (Elite India Org Team)
Email: team@eliteindia.org

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import inspect
import functools
from typing import Any, Callable, Dict, List, Optional, Union, get_type_hints
from collections.abc import Mapping, Sequence


class TypeValidationError(Exception):
    """Raised when runtime type validation fails"""
    pass


class RuntimeValidator:
    """Main class for runtime type validation"""
    
    @staticmethod
    def validate_type(value: Any, expected_type: Any, var_name: str = "value") -> bool:
        """Validate that value matches expected type"""
        try:
            if expected_type is None or expected_type == type(None):
                return value is None
            
            if expected_type == Any:
                return True
            
            # Handle basic types
            if expected_type in (int, float, str, bool, list, dict, tuple, set):
                if not isinstance(value, expected_type):
                    raise TypeValidationError(
                        f"{var_name} expected {expected_type.__name__}, got {type(value).__name__}"
                    )
                return True
            
            # Handle Optional types
            if hasattr(expected_type, '__origin__') and expected_type.__origin__ is Union:
                type_args = expected_type.__args__
                if len(type_args) == 2 and type(None) in type_args:
                    # This is Optional[T]
                    if value is None:
                        return True
                    non_none_type = next(t for t in type_args if t != type(None))
                    return RuntimeValidator.validate_type(value, non_none_type, var_name)
            
            # Handle List types
            if hasattr(expected_type, '__origin__') and expected_type.__origin__ in (list, List):
                if not isinstance(value, list):
                    raise TypeValidationError(
                        f"{var_name} expected list, got {type(value).__name__}"
                    )
                
                if hasattr(expected_type, '__args__') and expected_type.__args__:
                    element_type = expected_type.__args__[0]
                    for i, item in enumerate(value):
                        RuntimeValidator.validate_type(item, element_type, f"{var_name}[{i}]")
                
                return True
            
            # Handle Dict types  
            if hasattr(expected_type, '__origin__') and expected_type.__origin__ in (dict, Dict):
                if not isinstance(value, dict):
                    raise TypeValidationError(
                        f"{var_name} expected dict, got {type(value).__name__}"
                    )
                
                if hasattr(expected_type, '__args__') and len(expected_type.__args__) == 2:
                    key_type, value_type = expected_type.__args__
                    for k, v in value.items():
                        RuntimeValidator.validate_type(k, key_type, f"{var_name} key")
                        RuntimeValidator.validate_type(v, value_type, f"{var_name}[{k}]")
                
                return True
            
            # Handle custom classes
            if inspect.isclass(expected_type):
                if not isinstance(value, expected_type):
                    raise TypeValidationError(
                        f"{var_name} expected {expected_type.__name__}, got {type(value).__name__}"
                    )
                return True
            
            # Handle string type annotations
            if isinstance(expected_type, str):
                # Try to resolve the type name
                if expected_type in ('int', 'integer'):
                    return isinstance(value, int)
                elif expected_type in ('float', 'number'):
                    return isinstance(value, (int, float))
                elif expected_type in ('str', 'string'):
                    return isinstance(value, str)
                elif expected_type in ('bool', 'boolean'):
                    return isinstance(value, bool)
                elif expected_type == 'list':
                    return isinstance(value, list)
                elif expected_type == 'dict':
                    return isinstance(value, dict)
            
            return True
            
        except Exception as e:
            if isinstance(e, TypeValidationError):
                raise
            raise TypeValidationError(f"Type validation failed for {var_name}: {str(e)}")
    
    @staticmethod
    def validate_function_types(func: Callable) -> Callable:
        """Decorator to validate function parameter and return types"""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get type hints
            try:
                type_hints = get_type_hints(func)
            except:
                type_hints = {}
            
            # Get function signature
            sig = inspect.signature(func)
            
            # Validate parameters
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            for param_name, param_value in bound_args.arguments.items():
                if param_name in type_hints:
                    expected_type = type_hints[param_name]
                    RuntimeValidator.validate_type(param_value, expected_type, param_name)
            
            # Call the function
            result = func(*args, **kwargs)
            
            # Validate return type
            if 'return' in type_hints:
                return_type = type_hints['return']
                RuntimeValidator.validate_type(result, return_type, "return value")
            
            return result
        
        return wrapper


def validate_type(value: Any, expected_type: Any, var_name: str = "value") -> bool:
    """Convenience function for type validation"""
    return RuntimeValidator.validate_type(value, expected_type, var_name)


def runtime_check(func: Callable) -> Callable:
    """Decorator for runtime type checking of function parameters and return values"""
    return RuntimeValidator.validate_function_types(func)


class TypedProperty:
    """Property descriptor with runtime type checking"""
    
    def __init__(self, expected_type: Any, default: Any = None):
        self.expected_type = expected_type
        self.default = default
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f'_{name}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, self.default)
    
    def __set__(self, obj, value):
        if self.expected_type is not None:
            RuntimeValidator.validate_type(value, self.expected_type, self.name)
        setattr(obj, self.private_name, value)


def typed_property(expected_type: Any, default: Any = None) -> TypedProperty:
    """Create a typed property with runtime validation"""
    return TypedProperty(expected_type, default)


class StrictTypeMeta(type):
    """Metaclass that adds runtime type checking to all methods"""
    
    def __new__(mcs, name, bases, namespace, **kwargs):
        # Add type checking to all methods
        for attr_name, attr_value in namespace.items():
            if callable(attr_value) and not attr_name.startswith('__'):
                namespace[attr_name] = runtime_check(attr_value)
        
        return super().__new__(mcs, name, bases, namespace)


class StrictTypeClass(metaclass=StrictTypeMeta):
    """Base class for strict type checking"""
    pass