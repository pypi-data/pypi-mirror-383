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

import functools
import inspect
from typing import Any, Callable, TypeVar, cast
from enum import Enum


class AccessLevel(Enum):
    """Access level enumeration"""
    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"


class AccessViolationError(Exception):
    """Raised when access modifier rules are violated"""
    pass


F = TypeVar('F', bound=Callable[..., Any])


class AccessModifiers:
    """Main class for access modifier functionality"""
    
    @staticmethod
    def private(func: F) -> F:
        """Decorator for private methods/attributes"""
        func.__access_level__ = AccessLevel.PRIVATE
        func.__private_class__ = None  # Will be set when method is bound
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if args:  # Method call with self
                caller_frame = inspect.currentframe().f_back
                caller_locals = caller_frame.f_locals
                caller_self = caller_locals.get('self')
                
                # Get the class that defined this private method
                if not hasattr(func, '__private_class__') or func.__private_class__ is None:
                    func.__private_class__ = args[0].__class__
                
                # Check if caller is from the same class instance
                if caller_self is not args[0]:
                    raise AccessViolationError(
                        f"Cannot access private method '{func.__name__}' from outside the defining class"
                    )
            
            return func(*args, **kwargs)
        
        return cast(F, wrapper)
    
    @staticmethod
    def protected(func: F) -> F:
        """Decorator for protected methods/attributes"""
        func.__access_level__ = AccessLevel.PROTECTED
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if args:  # Method call with self
                caller_frame = inspect.currentframe().f_back
                caller_locals = caller_frame.f_locals
                caller_self = caller_locals.get('self')
                
                # Allow access from same class or subclasses
                if caller_self is not None:
                    method_class = args[0].__class__
                    caller_class = caller_self.__class__
                    
                    # Check if caller is from the same class hierarchy
                    if not (isinstance(caller_self, method_class) or isinstance(args[0], caller_class)):
                        raise AccessViolationError(
                            f"Cannot access protected method '{func.__name__}' from outside the class hierarchy"
                        )
            
            return func(*args, **kwargs)
        
        return cast(F, wrapper)
    
    @staticmethod  
    def public(func: F) -> F:
        """Decorator for public methods/attributes (default - mainly for documentation)"""
        func.__access_level__ = AccessLevel.PUBLIC
        return func
    
    @staticmethod
    def check_access(obj: Any, attr_name: str, caller_class: type = None) -> bool:
        """Check if access to attribute is allowed"""
        if not hasattr(obj, attr_name):
            return False
        
        attr = getattr(obj, attr_name)
        access_level = getattr(attr, '__access_level__', AccessLevel.PUBLIC)
        
        if access_level == AccessLevel.PUBLIC:
            return True
        
        if access_level == AccessLevel.PRIVATE:
            # Only allow access from the same class
            attr_class = getattr(attr, '__private_class__', obj.__class__)
            return caller_class is attr_class
        
        if access_level == AccessLevel.PROTECTED:
            # Allow access from same class or subclasses
            if caller_class is None:
                return False
            return issubclass(caller_class, obj.__class__) or issubclass(obj.__class__, caller_class)
        
        return False


# Convenience decorators
def private(func: F) -> F:
    """Decorator for private methods/attributes"""
    return AccessModifiers.private(func)


def protected(func: F) -> F:
    """Decorator for protected methods/attributes"""  
    return AccessModifiers.protected(func)


def public(func: F) -> F:
    """Decorator for public methods/attributes"""
    return AccessModifiers.public(func)


class AccessControlledMeta(type):
    """Metaclass that enforces access control on attribute access"""
    
    def __new__(mcs, name, bases, namespace, **kwargs):
        # Add access control to methods
        for attr_name, attr_value in namespace.items():
            if callable(attr_value) and not attr_name.startswith('__'):
                # Apply access modifier based on naming convention
                if attr_name.startswith('_' + name + '__'):
                    # Already name-mangled private
                    namespace[attr_name] = private(attr_value)
                elif attr_name.startswith('_'):
                    # Protected (single underscore)
                    namespace[attr_name] = protected(attr_value)
                else:
                    # Public
                    namespace[attr_name] = public(attr_value)
        
        return super().__new__(mcs, name, bases, namespace)


class PowerScriptClass(metaclass=AccessControlledMeta):
    """Base class for PowerScript classes with access control"""
    
    def __getattribute__(self, name: str) -> Any:
        """Override attribute access to enforce access modifiers"""
        try:
            attr = object.__getattribute__(self, name)
            
            # Check access level
            access_level = getattr(attr, '__access_level__', AccessLevel.PUBLIC)
            
            if access_level != AccessLevel.PUBLIC:
                # Get caller information
                caller_frame = inspect.currentframe().f_back
                caller_locals = caller_frame.f_locals
                caller_self = caller_locals.get('self')
                
                if access_level == AccessLevel.PRIVATE:
                    # Private - only accessible from same instance
                    if caller_self is not self:
                        raise AccessViolationError(
                            f"Cannot access private attribute '{name}' from outside the defining class"
                        )
                
                elif access_level == AccessLevel.PROTECTED:
                    # Protected - accessible from class hierarchy
                    if caller_self is None or not isinstance(caller_self, self.__class__):
                        if not (hasattr(caller_self, '__class__') and 
                               (issubclass(caller_self.__class__, self.__class__) or 
                                issubclass(self.__class__, caller_self.__class__))):
                            raise AccessViolationError(
                                f"Cannot access protected attribute '{name}' from outside the class hierarchy"
                            )
            
            return attr
        
        except AttributeError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")