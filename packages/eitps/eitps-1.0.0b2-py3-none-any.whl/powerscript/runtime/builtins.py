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

from typing import Any, List, Dict, Union, Optional
from .file_system import FileSystem, JSONFile, CSVFile, FileStream, FileError
import sys
import json
import math
import random
import time
import datetime
import re
import hashlib
import base64


class Console:
    """Console I/O operations"""
    
    @staticmethod
    def log(*args, sep: str = ' ', end: str = '\n'):
        """Print to console (equivalent to console.log)"""
        __builtins__['print'](*args, sep=sep, end=end)
    
    @staticmethod
    def error(*args, sep: str = ' ', end: str = '\n'):
        """Print to stderr"""
        __builtins__['print'](*args, sep=sep, end=end, file=sys.stderr)
    
    @staticmethod
    def warn(*args, sep: str = ' ', end: str = '\n'):
        """Print warning to stderr"""
        print("WARNING:", *args, sep=sep, end=end, file=sys.stderr)
    
    @staticmethod
    def input(prompt: str = "") -> str:
        """Get user input"""
        return __builtins__['input'](prompt)
    
    @staticmethod
    def clear():
        """Clear console (platform specific)"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')


class File:
    """File operations built-in class"""
    
    @staticmethod
    def read_text(path: str, encoding: str = 'utf-8') -> str:
        """Read file as text"""
        return FileSystem.read_text(path, encoding)
    
    @staticmethod
    def write_text(path: str, content: str, encoding: str = 'utf-8') -> None:
        """Write text to file"""
        FileSystem.write_text(path, content, encoding)
    
    @staticmethod
    def append_text(path: str, content: str, encoding: str = 'utf-8') -> None:
        """Append text to file"""
        FileSystem.append_text(path, content, encoding)
    
    @staticmethod
    def read_lines(path: str, encoding: str = 'utf-8') -> List[str]:
        """Read file as lines"""
        return FileSystem.read_lines(path, encoding)
    
    @staticmethod
    def write_lines(path: str, lines: List[str], encoding: str = 'utf-8') -> None:
        """Write lines to file"""
        FileSystem.write_lines(path, lines, encoding)
    
    @staticmethod
    def exists(path: str) -> bool:
        """Check if file exists"""
        return FileSystem.exists(path)
    
    @staticmethod
    def delete(path: str) -> None:
        """Delete file"""
        FileSystem.delete_file(path)
    
    @staticmethod
    def copy(src: str, dst: str) -> None:
        """Copy file"""
        FileSystem.copy_file(src, dst)
    
    @staticmethod
    def move(src: str, dst: str) -> None:
        """Move/rename file"""
        FileSystem.move_file(src, dst)
    
    @staticmethod
    def size(path: str) -> int:
        """Get file size"""
        return FileSystem.get_size(path)
    
    @staticmethod
    def modified_time(path: str) -> float:
        """Get last modified time"""
        return FileSystem.get_modified_time(path)
    
    @staticmethod
    def read_json(path: str) -> Any:
        """Read JSON file"""
        return JSONFile.read(path)
    
    @staticmethod
    def write_json(path: str, data: Any, indent: int = 2) -> None:
        """Write JSON file"""
        JSONFile.write(path, data, indent)
    
    @staticmethod
    def read_csv(path: str, has_header: bool = True) -> List[Dict[str, str]]:
        """Read CSV file"""
        return CSVFile.read(path, has_header)
    
    @staticmethod
    def write_csv(path: str, data: List[Dict[str, Any]], fieldnames: Optional[List[str]] = None) -> None:
        """Write CSV file"""
        CSVFile.write(path, data, fieldnames)


class Directory:
    """Directory operations built-in class"""
    
    @staticmethod
    def create(path: str) -> None:
        """Create directory"""
        FileSystem.create_directory(path)
    
    @staticmethod
    def delete(path: str, recursive: bool = False) -> None:
        """Delete directory"""
        FileSystem.delete_directory(path, recursive)
    
    @staticmethod
    def exists(path: str) -> bool:
        """Check if directory exists"""
        return FileSystem.is_directory(path)
    
    @staticmethod
    def list(path: str) -> List[str]:
        """List directory contents"""
        return FileSystem.list_directory(path)
    
    @staticmethod
    def list_files(path: str, pattern: str = "*") -> List[str]:
        """List files in directory"""
        return FileSystem.list_files(path, pattern)
    
    @staticmethod
    def list_directories(path: str) -> List[str]:
        """List subdirectories"""
        return FileSystem.list_directories(path)
    
    @staticmethod
    def current() -> str:
        """Get current directory"""
        return FileSystem.get_current_directory()
    
    @staticmethod
    def change(path: str) -> None:
        """Change current directory"""
        FileSystem.set_current_directory(path)


class Path:
    """Path manipulation utilities"""
    
    @staticmethod
    def join(*parts: str) -> str:
        """Join path components"""
        return FileSystem.join_path(*parts)
    
    @staticmethod
    def absolute(path: str) -> str:
        """Get absolute path"""
        return FileSystem.get_absolute_path(path)
    
    @staticmethod
    def parent(path: str) -> str:
        """Get parent directory"""
        return FileSystem.get_parent_directory(path)
    
    @staticmethod
    def filename(path: str) -> str:
        """Get filename"""
        return FileSystem.get_filename(path)
    
    @staticmethod
    def extension(path: str) -> str:
        """Get file extension"""
        return FileSystem.get_file_extension(path)
    
    @staticmethod
    def name_without_extension(path: str) -> str:
        """Get filename without extension"""
        return FileSystem.get_filename_without_extension(path)
    
    @staticmethod
    def exists(path: str) -> bool:
        """Check if path exists"""
        return FileSystem.exists(path)
    
    @staticmethod
    def is_file(path: str) -> bool:
        """Check if path is file"""
        return FileSystem.is_file(path)
    
    @staticmethod
    def is_directory(path: str) -> bool:
        """Check if path is directory"""
        return FileSystem.is_directory(path)


class Math:
    """Math utilities"""
    
    PI = math.pi
    E = math.e
    
    @staticmethod
    def abs(x: float) -> float:
        return abs(x)
    
    @staticmethod
    def ceil(x: float) -> int:
        return math.ceil(x)
    
    @staticmethod
    def floor(x: float) -> int:
        return math.floor(x)
    
    @staticmethod
    def round(x: float, digits: int = 0) -> float:
        return round(x, digits)
    
    @staticmethod
    def sqrt(x: float) -> float:
        return math.sqrt(x)
    
    @staticmethod
    def pow(x: float, y: float) -> float:
        return math.pow(x, y)
    
    @staticmethod
    def min(*args) -> float:
        return min(args)
    
    @staticmethod
    def max(*args) -> float:
        return max(args)
    
    @staticmethod
    def random() -> float:
        return random.random()
    
    @staticmethod
    def random_int(min_val: int, max_val: int) -> int:
        return random.randint(min_val, max_val)


class DateTime:
    """Date and time utilities"""
    
    @staticmethod
    def now() -> float:
        """Get current timestamp"""
        return time.time()
    
    @staticmethod
    def format(timestamp: float, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format timestamp as string"""
        return datetime.datetime.fromtimestamp(timestamp).strftime(format_str)
    
    @staticmethod
    def parse(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> float:
        """Parse date string to timestamp"""
        return datetime.datetime.strptime(date_str, format_str).timestamp()
    
    @staticmethod
    def sleep(seconds: float) -> None:
        """Sleep for specified seconds"""
        time.sleep(seconds)


class JSON:
    """JSON utilities"""
    
    @staticmethod
    def parse(json_str: str) -> Any:
        """Parse JSON string"""
        return json.loads(json_str)
    
    @staticmethod
    def stringify(obj: Any, indent: int = None) -> str:
        """Convert object to JSON string"""
        return json.dumps(obj, indent=indent, ensure_ascii=False)


class RegExp:
    """Regular expression utilities"""
    
    @staticmethod
    def match(pattern: str, text: str, flags: int = 0) -> Optional[List[str]]:
        """Find first match"""
        match = re.search(pattern, text, flags)
        return list(match.groups()) if match else None
    
    @staticmethod
    def match_all(pattern: str, text: str, flags: int = 0) -> List[List[str]]:
        """Find all matches"""
        return [list(match.groups()) for match in re.finditer(pattern, text, flags)]
    
    @staticmethod
    def replace(pattern: str, replacement: str, text: str, flags: int = 0) -> str:
        """Replace matches"""
        return re.sub(pattern, replacement, text, flags=flags)
    
    @staticmethod
    def split(pattern: str, text: str, flags: int = 0) -> List[str]:
        """Split by pattern"""
        return re.split(pattern, text, flags=flags)
    
    @staticmethod
    def test(pattern: str, text: str, flags: int = 0) -> bool:
        """Test if pattern matches"""
        return bool(re.search(pattern, text, flags))


class String:
    """String utilities with Python string methods"""
    
    @staticmethod
    def capitalize(s: str) -> str:
        """Capitalize first character and lowercase the rest"""
        return s.capitalize()
    
    @staticmethod
    def casefold(s: str) -> str:
        """Return casefolded string for case-insensitive comparisons"""
        return s.casefold()
    
    @staticmethod
    def center(s: str, width: int, fillchar: str = ' ') -> str:
        """Center string in a field of given width"""
        return s.center(width, fillchar)
    
    @staticmethod
    def count(s: str, sub: str, start: int = 0, end: int = None) -> int:
        """Count non-overlapping occurrences of substring"""
        return s.count(sub, start, end)
    
    @staticmethod
    def encode(s: str, encoding: str = 'utf-8', errors: str = 'strict') -> bytes:
        """Encode string using specified encoding"""
        return s.encode(encoding, errors)
    
    @staticmethod
    def endswith(s: str, suffix, start: int = 0, end: int = None) -> bool:
        """Check if string ends with specified suffix"""
        return s.endswith(suffix, start, end)
    
    @staticmethod
    def expandtabs(s: str, tabsize: int = 8) -> str:
        """Replace tabs with spaces"""
        return s.expandtabs(tabsize)
    
    @staticmethod
    def find(s: str, sub: str, start: int = 0, end: int = None) -> int:
        """Find first occurrence of substring"""
        return s.find(sub, start, end)
    
    @staticmethod
    def format(s: str, *args, **kwargs) -> str:
        """Format string with given arguments"""
        return s.format(*args, **kwargs)
    
    @staticmethod
    def format_map(s: str, mapping) -> str:
        """Format string using mapping"""
        return s.format_map(mapping)
    
    @staticmethod
    def index(s: str, sub: str, start: int = 0, end: int = None) -> int:
        """Find first occurrence of substring (raises ValueError if not found)"""
        return s.index(sub, start, end)
    
    @staticmethod
    def isalnum(s: str) -> bool:
        """Check if all characters are alphanumeric"""
        return s.isalnum()
    
    @staticmethod
    def isalpha(s: str) -> bool:
        """Check if all characters are alphabetic"""
        return s.isalpha()
    
    @staticmethod
    def isascii(s: str) -> bool:
        """Check if all characters are ASCII"""
        return s.isascii()
    
    @staticmethod
    def isdecimal(s: str) -> bool:
        """Check if all characters are decimal"""
        return s.isdecimal()
    
    @staticmethod
    def isdigit(s: str) -> bool:
        """Check if all characters are digits"""
        return s.isdigit()
    
    @staticmethod
    def isidentifier(s: str) -> bool:
        """Check if string is a valid identifier"""
        return s.isidentifier()
    
    @staticmethod
    def islower(s: str) -> bool:
        """Check if all cased characters are lowercase"""
        return s.islower()
    
    @staticmethod
    def isnumeric(s: str) -> bool:
        """Check if all characters are numeric"""
        return s.isnumeric()
    
    @staticmethod
    def isprintable(s: str) -> bool:
        """Check if all characters are printable"""
        return s.isprintable()
    
    @staticmethod
    def isspace(s: str) -> bool:
        """Check if all characters are whitespace"""
        return s.isspace()
    
    @staticmethod
    def istitle(s: str) -> bool:
        """Check if string is titlecased"""
        return s.istitle()
    
    @staticmethod
    def isupper(s: str) -> bool:
        """Check if all cased characters are uppercase"""
        return s.isupper()
    
    @staticmethod
    def join(s: str, iterable) -> str:
        """Join elements of iterable with string as separator"""
        return s.join(iterable)
    
    @staticmethod
    def ljust(s: str, width: int, fillchar: str = ' ') -> str:
        """Left-justify string in a field of given width"""
        return s.ljust(width, fillchar)
    
    @staticmethod
    def lower(s: str) -> str:
        """Convert to lowercase"""
        return s.lower()
    
    @staticmethod
    def lstrip(s: str, chars: str = None) -> str:
        """Remove leading whitespace or characters"""
        return s.lstrip(chars)
    
    @staticmethod
    def maketrans(x, y=None, z=None):
        """Create translation table for use with translate()"""
        return str.maketrans(x, y, z)
    
    @staticmethod
    def partition(s: str, sep: str):
        """Partition string at first occurrence of separator"""
        return s.partition(sep)
    
    @staticmethod
    def removeprefix(s: str, prefix: str) -> str:
        """Remove prefix from string (Python 3.9+)"""
        if hasattr(str, 'removeprefix'):
            return s.removeprefix(prefix)
        return s[len(prefix):] if s.startswith(prefix) else s
    
    @staticmethod
    def removesuffix(s: str, suffix: str) -> str:
        """Remove suffix from string (Python 3.9+)"""
        if hasattr(str, 'removesuffix'):
            return s.removesuffix(suffix)
        return s[:-len(suffix)] if s.endswith(suffix) else s
    
    @staticmethod
    def replace(s: str, old: str, new: str, count: int = -1) -> str:
        """Replace occurrences of substring"""
        return s.replace(old, new, count)
    
    @staticmethod
    def rfind(s: str, sub: str, start: int = 0, end: int = None) -> int:
        """Find last occurrence of substring"""
        return s.rfind(sub, start, end)
    
    @staticmethod
    def rindex(s: str, sub: str, start: int = 0, end: int = None) -> int:
        """Find last occurrence of substring (raises ValueError if not found)"""
        return s.rindex(sub, start, end)
    
    @staticmethod
    def rjust(s: str, width: int, fillchar: str = ' ') -> str:
        """Right-justify string in a field of given width"""
        return s.rjust(width, fillchar)
    
    @staticmethod
    def rpartition(s: str, sep: str):
        """Partition string at last occurrence of separator"""
        return s.rpartition(sep)
    
    @staticmethod
    def rsplit(s: str, sep: str = None, maxsplit: int = -1):
        """Split string from the right"""
        return s.rsplit(sep, maxsplit)
    
    @staticmethod
    def rstrip(s: str, chars: str = None) -> str:
        """Remove trailing whitespace or characters"""
        return s.rstrip(chars)
    
    @staticmethod
    def split(s: str, sep: str = None, maxsplit: int = -1):
        """Split string into list"""
        return s.split(sep, maxsplit)
    
    @staticmethod
    def splitlines(s: str, keepends: bool = False):
        """Split string at line boundaries"""
        return s.splitlines(keepends)
    
    @staticmethod
    def startswith(s: str, prefix, start: int = 0, end: int = None) -> bool:
        """Check if string starts with specified prefix"""
        return s.startswith(prefix, start, end)
    
    @staticmethod
    def strip(s: str, chars: str = None) -> str:
        """Remove leading and trailing whitespace or characters"""
        return s.strip(chars)
    
    @staticmethod
    def swapcase(s: str) -> str:
        """Swap case of all cased characters"""
        return s.swapcase()
    
    @staticmethod
    def title(s: str) -> str:
        """Convert to titlecase"""
        return s.title()
    
    @staticmethod
    def translate(s: str, table) -> str:
        """Apply translation table to string"""
        return s.translate(table)
    
    @staticmethod
    def upper(s: str) -> str:
        """Convert to uppercase"""
        return s.upper()
    
    @staticmethod
    def zfill(s: str, width: int) -> str:
        """Pad numeric string with zeros on the left"""
        return s.zfill(width)


class Array:
    """Array/List utilities with Python list methods"""
    
    @staticmethod
    def append(arr: list, item) -> None:
        """Add item to end of array"""
        arr.append(item)
    
    @staticmethod
    def clear(arr: list) -> None:
        """Remove all items from array"""
        arr.clear()
    
    @staticmethod
    def copy(arr: list) -> list:
        """Return shallow copy of array"""
        return arr.copy()
    
    @staticmethod
    def count(arr: list, item) -> int:
        """Count occurrences of item in array"""
        return arr.count(item)
    
    @staticmethod
    def extend(arr: list, iterable) -> None:
        """Extend array with items from iterable"""
        arr.extend(iterable)
    
    @staticmethod
    def index(arr: list, item, start: int = 0, end: int = None) -> int:
        """Find first index of item"""
        return arr.index(item, start, end)
    
    @staticmethod
    def insert(arr: list, index: int, item) -> None:
        """Insert item at specified index"""
        arr.insert(index, item)
    
    @staticmethod
    def pop(arr: list, index: int = -1):
        """Remove and return item at index (default last)"""
        return arr.pop(index)
    
    @staticmethod
    def remove(arr: list, item) -> None:
        """Remove first occurrence of item"""
        arr.remove(item)
    
    @staticmethod
    def reverse(arr: list) -> None:
        """Reverse array in place"""
        arr.reverse()
    
    @staticmethod
    def sort(arr: list, key=None, reverse: bool = False) -> None:
        """Sort array in place"""
        arr.sort(key=key, reverse=reverse)
    
    # Additional utility methods
    @staticmethod
    def join(arr: list, separator: str = ',') -> str:
        """Join array elements into string"""
        return separator.join(str(x) for x in arr)
    
    @staticmethod
    def slice(arr: list, start: int = 0, end: int = None, step: int = 1) -> list:
        """Return slice of array"""
        return arr[start:end:step]
    
    @staticmethod
    def includes(arr: list, item) -> bool:
        """Check if array contains item"""
        return item in arr
    
    @staticmethod
    def indexOf(arr: list, item) -> int:
        """Find index of item (-1 if not found)"""
        try:
            return arr.index(item)
        except ValueError:
            return -1
    
    @staticmethod
    def lastIndexOf(arr: list, item) -> int:
        """Find last index of item (-1 if not found)"""
        try:
            for i in range(len(arr) - 1, -1, -1):
                if arr[i] == item:
                    return i
            return -1
        except:
            return -1
    
    @staticmethod
    def push(arr: list, *items) -> int:
        """Add items to end and return new length"""
        for item in items:
            arr.append(item)
        return len(arr)
    
    @staticmethod
    def unshift(arr: list, *items) -> int:
        """Add items to beginning and return new length"""
        for i, item in enumerate(items):
            arr.insert(i, item)
        return len(arr)
    
    @staticmethod
    def shift(arr: list):
        """Remove and return first item"""
        return arr.pop(0) if arr else None
    
    @staticmethod
    def splice(arr: list, start: int, delete_count: int = None, *items) -> list:
        """Remove elements and optionally insert new ones"""
        if delete_count is None:
            delete_count = len(arr) - start
        
        # Get removed items
        removed = arr[start:start + delete_count]
        
        # Remove items
        del arr[start:start + delete_count]
        
        # Insert new items
        for i, item in enumerate(items):
            arr.insert(start + i, item)
        
        return removed


class Dict:
    """Dictionary utilities with Python dict methods"""
    
    @staticmethod
    def clear(d: dict) -> None:
        """Remove all items from dictionary"""
        d.clear()
    
    @staticmethod
    def copy(d: dict) -> dict:
        """Return shallow copy of dictionary"""
        return d.copy()
    
    @staticmethod
    def fromkeys(keys, value=None) -> dict:
        """Create dictionary from keys with same value"""
        return dict.fromkeys(keys, value)
    
    @staticmethod
    def get(d: dict, key, default=None):
        """Get value for key, return default if not found"""
        return d.get(key, default)
    
    @staticmethod
    def items(d: dict):
        """Return dictionary items as (key, value) pairs"""
        return d.items()
    
    @staticmethod
    def keys(d: dict):
        """Return dictionary keys"""
        return d.keys()
    
    @staticmethod
    def pop(d: dict, key, default=None):
        """Remove key and return its value"""
        return d.pop(key, default)
    
    @staticmethod
    def popitem(d: dict):
        """Remove and return last (key, value) pair"""
        return d.popitem()
    
    @staticmethod
    def setdefault(d: dict, key, default=None):
        """Get key value, set to default if not exists"""
        return d.setdefault(key, default)
    
    @staticmethod
    def update(d: dict, other=None, **kwargs) -> None:
        """Update dictionary with another dict or kwargs"""
        if other:
            d.update(other)
        if kwargs:
            d.update(kwargs)
    
    @staticmethod
    def values(d: dict):
        """Return dictionary values"""
        return d.values()
    
    # Additional utility methods
    @staticmethod
    def has_key(d: dict, key) -> bool:
        """Check if dictionary has key"""
        return key in d
    
    @staticmethod
    def merge(d1: dict, d2: dict) -> dict:
        """Merge two dictionaries into new one"""
        result = d1.copy()
        result.update(d2)
        return result
    
    @staticmethod
    def filter_keys(d: dict, predicate) -> dict:
        """Filter dictionary by key predicate"""
        return {k: v for k, v in d.items() if predicate(k)}
    
    @staticmethod
    def filter_values(d: dict, predicate) -> dict:
        """Filter dictionary by value predicate"""
        return {k: v for k, v in d.items() if predicate(v)}
    
    @staticmethod
    def map_values(d: dict, func) -> dict:
        """Map function over dictionary values"""
        return {k: func(v) for k, v in d.items()}
    
    @staticmethod
    def map_keys(d: dict, func) -> dict:
        """Map function over dictionary keys"""
        return {func(k): v for k, v in d.items()}


class Set:
    """Set utilities with Python set methods"""
    
    @staticmethod
    def add(s: set, item) -> None:
        """Add item to set"""
        s.add(item)
    
    @staticmethod
    def clear(s: set) -> None:
        """Remove all items from set"""
        s.clear()
    
    @staticmethod
    def copy(s: set) -> set:
        """Return shallow copy of set"""
        return s.copy()
    
    @staticmethod
    def difference(s: set, *others) -> set:
        """Return set difference"""
        return s.difference(*others)
    
    @staticmethod
    def difference_update(s: set, *others) -> None:
        """Update set with difference"""
        s.difference_update(*others)
    
    @staticmethod
    def discard(s: set, item) -> None:
        """Remove item from set if present"""
        s.discard(item)
    
    @staticmethod
    def intersection(s: set, *others) -> set:
        """Return set intersection"""
        return s.intersection(*others)
    
    @staticmethod
    def intersection_update(s: set, *others) -> None:
        """Update set with intersection"""
        s.intersection_update(*others)
    
    @staticmethod
    def isdisjoint(s: set, other) -> bool:
        """Check if sets have no common elements"""
        return s.isdisjoint(other)
    
    @staticmethod
    def issubset(s: set, other) -> bool:
        """Check if set is subset of other"""
        return s.issubset(other)
    
    @staticmethod
    def issuperset(s: set, other) -> bool:
        """Check if set is superset of other"""
        return s.issuperset(other)
    
    @staticmethod
    def pop(s: set):
        """Remove and return arbitrary item"""
        return s.pop()
    
    @staticmethod
    def remove(s: set, item) -> None:
        """Remove item from set (raises KeyError if not found)"""
        s.remove(item)
    
    @staticmethod
    def symmetric_difference(s: set, other) -> set:
        """Return symmetric difference"""
        return s.symmetric_difference(other)
    
    @staticmethod
    def symmetric_difference_update(s: set, other) -> None:
        """Update set with symmetric difference"""
        s.symmetric_difference_update(other)
    
    @staticmethod
    def union(s: set, *others) -> set:
        """Return set union"""
        return s.union(*others)
    
    @staticmethod
    def update(s: set, *others) -> None:
        """Update set with union"""
        s.update(*others)
    
    # Additional utility methods
    @staticmethod
    def contains(s: set, item) -> bool:
        """Check if set contains item"""
        return item in s
    
    @staticmethod
    def size(s: set) -> int:
        """Get size of set"""
        return len(s)
    
    @staticmethod
    def to_list(s: set) -> list:
        """Convert set to list"""
        return list(s)


# Built-in function wrappers for PowerScript
def assert_func(condition, message=None):
    """Assert condition is true"""
    assert condition, message

def type_func(obj):
    """Get type of object"""
    return __builtins__['type'](obj)

def isinstance_func(obj, class_or_tuple):
    """Check if object is instance of class"""
    return __builtins__['isinstance'](obj, class_or_tuple)

def hasattr_func(obj, name):
    """Check if object has attribute"""
    return __builtins__['hasattr'](obj, name)

def getattr_func(obj, name, default=None):
    """Get attribute from object"""
    return __builtins__['getattr'](obj, name, default)

def setattr_func(obj, name, value):
    """Set attribute on object"""
    __builtins__['setattr'](obj, name, value)

def delattr_func(obj, name):
    """Delete attribute from object"""
    __builtins__['delattr'](obj, name)

def dir_func(obj=None):
    """Get list of attributes"""
    return __builtins__['dir'](obj)

def vars_func(obj=None):
    """Get __dict__ of object"""
    return __builtins__['vars'](obj) if obj is not None else {}

def id_func(obj):
    """Get identity of object"""
    return __builtins__['id'](obj)

def hash_func(obj):
    """Get hash of object"""
    return __builtins__['hash'](obj)

def repr_func(obj):
    """Get string representation"""
    return __builtins__['repr'](obj)

def abs_func(x):
    """Get absolute value"""
    return abs(x)

def all_func(iterable):
    """Check if all elements are true"""
    return all(iterable)

def any_func(iterable):
    """Check if any element is true"""
    return any(iterable)

def min_func(*args, **kwargs):
    """Get minimum value"""
    return __builtins__['min'](*args, **kwargs)

def max_func(*args, **kwargs):
    """Get maximum value"""
    return __builtins__['max'](*args, **kwargs)

def sum_func(iterable, start=0):
    """Sum elements"""
    return __builtins__['sum'](iterable, start)

def sorted_func(iterable, key=None, reverse=False):
    """Sort iterable"""
    return __builtins__['sorted'](iterable, key=key, reverse=reverse)

def reversed_func(seq):
    """Reverse sequence"""
    return __builtins__['reversed'](seq)

def enumerate_func(iterable, start=0):
    """Enumerate iterable"""
    return __builtins__['enumerate'](iterable, start)

def zip_func(*iterables):
    """Zip iterables"""
    return __builtins__['zip'](*iterables)

def map_func(func, *iterables):
    """Map function over iterables"""
    return __builtins__['map'](func, *iterables)

def filter_func(func, iterable):
    """Filter iterable"""
    return __builtins__['filter'](func, iterable)

def range_func(*args):
    """Create range object"""
    return __builtins__['range'](*args)

def list_func(iterable=None):
    """Create list"""
    return list(iterable) if iterable is not None else []

def tuple_func(iterable=None):
    """Create tuple"""
    return tuple(iterable) if iterable is not None else ()

def set_func(iterable=None):
    """Create set"""
    return set(iterable) if iterable is not None else set()

def dict_func(*args, **kwargs):
    """Create dictionary"""
    return dict(*args, **kwargs)

def frozenset_func(iterable=None):
    """Create frozenset"""
    return frozenset(iterable) if iterable is not None else frozenset()

def bytearray_func(source=None, encoding=None, errors=None):
    """Create bytearray"""
    if source is None:
        return bytearray()
    elif isinstance(source, str):
        return bytearray(source, encoding or 'utf-8', errors or 'strict')
    else:
        return bytearray(source)

def bytes_func(source=None, encoding=None, errors=None):
    """Create bytes"""
    if source is None:
        return bytes()
    elif isinstance(source, str):
        return bytes(source, encoding or 'utf-8', errors or 'strict')
    else:
        return bytes(source)

def memoryview_func(obj):
    """Create memoryview"""
    return memoryview(obj)

def slice_func(*args):
    """Create slice"""
    return slice(*args)

def complex_func(real=0, imag=0):
    """Create complex number"""
    return complex(real, imag)

def round_func(number, ndigits=None):
    """Round number"""
    return round(number, ndigits) if ndigits is not None else round(number)

def pow_func(base, exp, mod=None):
    """Power function"""
    return pow(base, exp, mod)

def divmod_func(a, b):
    """Division and modulo"""
    return divmod(a, b)

def bin_func(x):
    """Binary representation"""
    return bin(x)

def oct_func(x):
    """Octal representation"""
    return oct(x)

def hex_func(x):
    """Hexadecimal representation"""
    return hex(x)

def ord_func(c):
    """Get unicode code point"""
    return ord(c)

def chr_func(i):
    """Get character from code point"""
    return chr(i)

def ascii_func(obj):
    """ASCII representation"""
    return ascii(obj)

def format_func(value, format_spec=''):
    """Format value"""
    return format(value, format_spec)

def eval_func(expression, globals=None, locals=None):
    """Evaluate expression"""
    return eval(expression, globals, locals)

def exec_func(object, globals=None, locals=None):
    """Execute code"""
    exec(object, globals, locals)

def compile_func(source, filename, mode, flags=0, dont_inherit=False, optimize=-1):
    """Compile source"""
    return compile(source, filename, mode, flags, dont_inherit, optimize)

def open_func(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
    """Open file"""
    import builtins
    return builtins.open(file, mode, buffering, encoding, errors, newline, closefd, opener)

def callable_func(obj):
    """Check if object is callable"""
    return callable(obj)

def classmethod_func(func):
    """Convert function to class method"""
    return classmethod(func)

def globals_func():
    """Get global symbol table"""
    return globals()

def help_func(obj=None):
    """Built-in help system"""
    if obj is None:
        print("Welcome to PowerScript help system!")
        print("Use help(object) to get help on any object.")
    else:
        help(obj)

def issubclass_func(class_or_tuple, classinfo):
    """Check subclass relationship"""
    return issubclass(class_or_tuple, classinfo)

def iter_func(iterable, sentinel=None):
    """Create iterator"""
    if sentinel is None:
        return iter(iterable)
    else:
        return iter(iterable, sentinel)

def locals_func():
    """Get local symbol table"""
    return locals()

def next_func(iterator, default=None):
    """Get next item from iterator"""
    if default is None:
        return next(iterator)
    else:
        return next(iterator, default)

def object_func():
    """Create new object"""
    return object()

def property_func(fget=None, fset=None, fdel=None, doc=None):
    """Create property"""
    return property(fget, fset, fdel, doc)

def staticmethod_func(func):
    """Convert function to static method"""
    return __builtins__['staticmethod'](func)

def super_func(*args, **kwargs):
    """Access parent class"""
    return super(*args, **kwargs)


# Global built-in objects
_fs = FileSystem()
_console = Console()

class Database:
    """Simple database interface using SQLite"""
    
    def __init__(self, db_path=":memory:"):
        """Initialize database connection"""
        import sqlite3
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def execute(self, query, params=None):
        """Execute SQL query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            return f"Error: {e}"
    
    def commit(self):
        """Commit changes"""
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        self.conn.close()


class Crypto:
    """Basic cryptography utilities"""
    
    @staticmethod
    def hash_sha256(data):
        """SHA256 hash"""
        try:
            data = data.encode('utf-8')
        except:
            pass
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def hash_md5(data):
        """MD5 hash"""
        try:
            data = data.encode('utf-8')
        except:
            pass
        return hashlib.md5(data).hexdigest()
    
    @staticmethod
    def base64_encode(data):
        """Base64 encode"""
        try:
            data = data.encode('utf-8')
        except:
            pass
        return base64.b64encode(data).decode('utf-8')
    
    @staticmethod
    def base64_decode(data):
        """Base64 decode"""
        return base64.b64decode(data).decode('utf-8')


class Network:
    """Simple networking interface"""
    
    @staticmethod
    def get(url, headers=None):
        """HTTP GET request"""
        try:
            import urllib.request
            import json
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            return f"Error: {e}"
    
    @staticmethod
    def post(url, data=None, headers=None):
        """HTTP POST request"""
        try:
            import urllib.request
            import urllib.parse
            import json
            if isinstance(data, dict):
                data = json.dumps(data).encode('utf-8')
                if not headers:
                    headers = {'Content-Type': 'application/json'}
            elif isinstance(data, str):
                data = data.encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers or {}, method='POST')
            with urllib.request.urlopen(req) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            return f"Error: {e}"
    
    @staticmethod
    def download(url, filename):
        """Download file from URL"""
        try:
            import urllib.request
            urllib.request.urlretrieve(url, filename)
            return True
        except Exception as e:
            return f"Error: {e}"


class Test:
    """Simple testing framework"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
    
    def assert_equal(self, actual, expected, message=""):
        """Assert two values are equal"""
        self.tests_run += 1
        if actual == expected:
            self.tests_passed += 1
            print(f"✓ PASS: {message}")
        else:
            self.tests_failed += 1
            print(f"✗ FAIL: {message} - Expected {expected}, got {actual}")
    
    def assert_true(self, condition, message=""):
        """Assert condition is true"""
        self.assert_equal(condition, True, message)
    
    def assert_false(self, condition, message=""):
        """Assert condition is false"""
        self.assert_equal(condition, False, message)
    
    def assert_raises(self, exception_type, func, message=""):
        """Assert that function raises specific exception"""
        self.tests_run += 1
        try:
            func()
            self.tests_failed += 1
            print(f"✗ FAIL: {message} - Expected {exception_type.__name__} but no exception raised")
        except exception_type:
            self.tests_passed += 1
            print(f"✓ PASS: {message}")
        except Exception as e:
            self.tests_failed += 1
            print(f"✗ FAIL: {message} - Expected {exception_type.__name__} but got {type(e).__name__}")
    
    def run(self):
        """Run all tests and print summary"""
        print(f"\nTest Results: {self.tests_passed}/{self.tests_run} passed, {self.tests_failed} failed")
        return self.tests_failed == 0


class GUI:
    """Simple GUI interface using Tkinter"""
    
    def __init__(self):
        self.root = None
        self.widgets = {}
    
    def create_window(self, title="PowerScript GUI", width=400, height=300):
        """Create main window"""
        try:
            import tkinter as tk
            self.root = tk.Tk()
            self.root.title(title)
            self.root.geometry(f"{width}x{height}")
            return self.root
        except ImportError:
            raise Exception("Tkinter not available. Install tkinter for GUI support.")
    
    def add_button(self, text, command=None, x=10, y=10):
        """Add button to window"""
        if not self.root:
            self.create_window()
        import tkinter as tk
        button = tk.Button(self.root, text=text, command=command)
        button.place(x=x, y=y)
        return button
    
    def add_label(self, text, x=10, y=50):
        """Add label to window"""
        if not self.root:
            self.create_window()
        import tkinter as tk
        label = tk.Label(self.root, text=text)
        label.place(x=x, y=y)
        return label
    
    def add_entry(self, x=10, y=80, width=20):
        """Add text entry field"""
        if not self.root:
            self.create_window()
        import tkinter as tk
        entry = tk.Entry(self.root, width=width)
        entry.place(x=x, y=y)
        return entry
    
    def run(self):
        """Start GUI event loop"""
        if self.root:
            self.root.mainloop()
    
    def close(self):
        """Close GUI window"""
        if self.root:
            self.root.destroy()


class MathStats:
    """Mathematics and statistics utilities"""
    
    @staticmethod
    def mean(data):
        """Calculate mean of data"""
        return __builtins__['sum'](data) / __builtins__['len'](data)
    
    @staticmethod
    def median(data):
        """Calculate median of data"""
        sorted_data = __builtins__['sorted'](data)
        n = __builtins__['len'](sorted_data)
        if n % 2 == 0:
            return (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
        else:
            return sorted_data[n//2]
    
    @staticmethod
    def std(data):
        """Calculate standard deviation"""
        # Avoid recursion by using local calculation
        mean_val = __builtins__['sum'](data) / __builtins__['len'](data)
        variance = __builtins__['sum']((x - mean_val) ** 2 for x in data) / __builtins__['len'](data)
        return variance ** 0.5
    
    @staticmethod
    def linspace(start, stop, num=50):
        """Create evenly spaced numbers"""
        step = (stop - start) / (num - 1)
        return [start + i * step for i in __builtins__['range'](num)]
    
    @staticmethod
    def arange(start, stop=None, step=1):
        """Create array with range"""
        if stop is None:
            stop = start
            start = 0
        return __builtins__['list'](__builtins__['range'](int(start), int(stop), int(step)))


BUILT_IN_GLOBALS = {
    # File system operations  
    'FileSystem': FileSystem,
    'file_write': _fs.write_text,
    'file_read': _fs.read_text,
    'file_append': _fs.append_text,
    'file_exists': _fs.exists,
    'file_delete': _fs.delete_file,
    'file_copy': _fs.copy_file,
    'file_move': _fs.move_file,
    'file_size': _fs.get_size,
    'file_modified_time': _fs.get_modified_time,
    'file_stream': FileStream,
    'dir_create': _fs.create_directory,
    'dir_delete': _fs.delete_directory,
    'dir_exists': _fs.exists,
    'dir_list': _fs.list_directory,
    'path_join': _fs.join_path,
    'path_absolute': _fs.get_absolute_path,
    'temp_file_create': _fs.create_temp_file,
    'temp_dir_create': _fs.create_temp_directory,
    'json_write': JSONFile.write,
    'json_read': JSONFile.read,
    'csv_write': CSVFile.write,
    'csv_read': CSVFile.read,
    
    # Classes
    'Console': Console,
    'File': File,
    'Directory': Directory,
    'Path': Path,
    'Math': Math,
    'DateTime': DateTime,
    'JSON': JSON,
    'RegExp': RegExp,
    'String': String,
    'Array': Array,
    'Dict': Dict,
    'Set': Set,
    'FileStream': FileStream,
    'FileError': FileError,
    'Database': Database,
    'GUI': GUI,
    'Network': Network,
    'Crypto': Crypto,
    'Test': Test,
    'MathStats': MathStats,
    
    # Core Python built-in functions
    'console': _console,
    'print': print,
    'input': input,
    'len': len,
    'str': str,
    'int': int,
    'float': float,
    'bool': bool,
    'assert': assert_func,
    'type': type_func,
    'isinstance': isinstance_func,
    'hasattr': hasattr_func,
    'getattr': getattr_func,
    'setattr': setattr_func,
    'delattr': delattr_func,
    'dir': dir_func,
    'vars': vars_func,
    'id': id_func,
    'hash': hash_func,
    'repr': repr_func,
    'abs': abs_func,
    'all': all_func,
    'any': any_func,
    'min': min_func,
    'max': max_func,
    'sum': sum_func,
    'sorted': sorted_func,
    'reversed': reversed_func,
    'enumerate': enumerate_func,
    'zip': zip_func,
    'map': map_func,
    'filter': filter_func,
    'range': range_func,
    'list': list_func,
    'tuple': tuple_func,
    'set': set_func,
    'dict': dict_func,
    'frozenset': frozenset_func,
    'bytearray': bytearray_func,
    'bytes': bytes_func,
    'memoryview': memoryview_func,
    'slice': slice_func,
    'complex': complex_func,
    'round': round_func,
    'pow': pow_func,
    'divmod': divmod_func,
    'bin': bin_func,
    'oct': oct_func,
    'hex': hex_func,
    'ord': ord_func,
    'chr': chr_func,
    'ascii': ascii_func,
    'format': format_func,
    'eval': eval_func,
    'exec': exec_func,
    'compile': compile_func,
    'open': open_func,
    'callable': callable_func,
    'classmethod': classmethod_func,
    'globals': globals_func,
    'help': help_func,
    'issubclass': issubclass_func,
    'iter': iter_func,
    'locals': locals_func,
    'next': next_func,
    'object': object_func,
    'property': property_func,
    'staticmethod': staticmethod_func,
    'super': super_func,
    
    # Legacy range function (keeping for compatibility)  
    'range': range,
    
    # Constants
    'PI': math.pi,
    'E': math.e,
    'Infinity': float('inf'),
    'NaN': float('nan'),
    
    # Standard Library Modules (Phase 4 - Standard Library Access)
    'sys': sys,
    'math': math,
    'random': random,
    'time': time,
    'datetime': datetime,
    'json': json,
    're': re,
    'os': __import__('os'),
    'collections': __import__('collections'),
    'itertools': __import__('itertools'),
    'functools': __import__('functools'),
    'operator': __import__('operator'),
    'pathlib': __import__('pathlib'),
    'urllib': __import__('urllib'),
    'http': __import__('http'),
    'socket': __import__('socket'),
    'threading': __import__('threading'),
    'multiprocessing': __import__('multiprocessing'),
    'subprocess': __import__('subprocess'),
    'uuid': __import__('uuid'),
    'hashlib': __import__('hashlib'),
    'base64': __import__('base64'),
    'csv': __import__('csv'),
    'xml': __import__('xml'),
    'sqlite3': __import__('sqlite3'),
    'pickle': __import__('pickle'),
    'copy': __import__('copy'),
    'weakref': __import__('weakref'),
    'gc': __import__('gc'),
    'inspect': __import__('inspect'),
    'logging': __import__('logging'),
    'warnings': __import__('warnings'),
    'tempfile': __import__('tempfile'),
    'shutil': __import__('shutil'),
    'glob': __import__('glob'),
    'fnmatch': __import__('fnmatch'),
    'stat': __import__('stat'),
    'platform': __import__('platform'),
    'getpass': __import__('getpass'),
    'argparse': __import__('argparse'),
    'configparser': __import__('configparser'),
}

# Python package import system
class PackageImporter:
    """Allows PowerScript to import and use Python packages"""
    
    @staticmethod
    def import_package(package_name: str, alias: str = None):
        """Import a Python package for use in PowerScript"""
        try:
            if '.' in package_name:
                # Handle submodule imports like numpy.random
                parts = package_name.split('.')
                module = __import__(package_name, fromlist=[parts[-1]])
            else:
                module = __import__(package_name)
            
            name = alias if alias else package_name.split('.')[-1]
            return {name: module}
        except ImportError as e:
            raise ImportError(f"Cannot import package '{package_name}': {str(e)}")
    
    @staticmethod
    def import_from(package_name: str, *items, alias_dict=None):
        """Import specific items from a Python package"""
        try:
            module = __import__(package_name, fromlist=items)
            result = {}
            
            for item in items:
                if hasattr(module, item):
                    attr = getattr(module, item)
                    name = alias_dict.get(item, item) if alias_dict else item
                    result[name] = attr
                else:
                    raise AttributeError(f"Module '{package_name}' has no attribute '{item}'")
            
            return result
        except ImportError as e:
            raise ImportError(f"Cannot import from package '{package_name}': {str(e)}")

# Package importer functions
def ps_import(package_name: str, alias: str = None):
    """Import a Python package"""
    return PackageImporter.import_package(package_name, alias)

def ps_from_import(package_name: str, *items, **aliases):
    """Import specific items from a Python package"""
    return PackageImporter.import_from(package_name, *items, alias_dict=aliases)

# Add package import functions to built-ins
BUILT_IN_GLOBALS.update({
    'ps_import': ps_import,
    'ps_from_import': ps_from_import,
    'PackageImporter': PackageImporter,
})

# Commonly used Python packages - auto-imported for convenience
try:
    import sys
    import os
    import re
    import json
    import math
    import random
    import datetime
    import time
    import collections
    import itertools
    import functools
    import operator
    import urllib.parse
    import urllib.request
    import base64
    import hashlib
    import uuid
    import threading
    import multiprocessing
    import asyncio
    import pathlib
    
    # Add common packages to built-ins
    BUILT_IN_GLOBALS.update({
        'sys': sys,
        'os': os,
        're': re,
        'json': json,
        'math': math,
        'random': random,
        'datetime': datetime,
        'time': time,
        'collections': collections,
        'itertools': itertools,
        'functools': functools,
        'operator': operator,
        'urllib': urllib,
        'base64': base64,
        'hashlib': hashlib,
        'uuid': uuid,
        'threading': threading,
        'multiprocessing': multiprocessing,
        'asyncio': asyncio,
        'pathlib': pathlib,
    })
    
except ImportError:
    # Some packages might not be available in all Python installations
    pass

# Try to import popular third-party packages if available
try:
    import numpy as np
    BUILT_IN_GLOBALS['numpy'] = np
    BUILT_IN_GLOBALS['np'] = np
except ImportError:
    pass

try:
    import pandas as pd
    BUILT_IN_GLOBALS['pandas'] = pd
    BUILT_IN_GLOBALS['pd'] = pd
except ImportError:
    pass

try:
    import requests
    BUILT_IN_GLOBALS['requests'] = requests
except ImportError:
    pass

# Additional modules
from .database import Database, create_database
# from .gui import Window, create_window  # Tkinter not available
# from .networking import HTTPClient, create_http_client

BUILT_IN_GLOBALS['Database'] = Database
BUILT_IN_GLOBALS['create_database'] = create_database
# BUILT_IN_GLOBALS['Window'] = Window
# BUILT_IN_GLOBALS['create_window'] = create_window
# # BUILT_IN_GLOBALS['HTTPClient'] = HTTPClient
# BUILT_IN_GLOBALS['create_http_client'] = create_http_client

try:
    import matplotlib.pyplot as plt
    BUILT_IN_GLOBALS['matplotlib'] = plt
    BUILT_IN_GLOBALS['plt'] = plt
except ImportError:
    pass

# Export all built-ins to module globals
globals().update(BUILT_IN_GLOBALS)

class PackageManager:
    """Package management utilities (pip-like functionality)"""
    
    @staticmethod
    def install(package_name: str, version: str = None, upgrade: bool = False) -> bool:
        """Install a Python package using pip"""
        import subprocess
        import sys
        
        try:
            cmd = [sys.executable, '-m', 'pip', 'install']
            if upgrade:
                cmd.append('--upgrade')
            if version:
                cmd.append(f"{package_name}=={version}")
            else:
                cmd.append(package_name)
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ Successfully installed {package_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package_name}: {e.stderr}")
            return False
        except Exception as e:
            print(f"✗ Error installing {package_name}: {str(e)}")
            return False
    
    @staticmethod
    def uninstall(package_name: str) -> bool:
        """Uninstall a Python package using pip"""
        import subprocess
        import sys
        
        try:
            cmd = [sys.executable, '-m', 'pip', 'uninstall', '-y', package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ Successfully uninstalled {package_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to uninstall {package_name}: {e.stderr}")
            return False
        except Exception as e:
            print(f"✗ Error uninstalling {package_name}: {str(e)}")
            return False
    
    @staticmethod
    def list_installed() -> list:
        """List all installed packages"""
        import subprocess
        import sys
        
        try:
            cmd = [sys.executable, '-m', 'pip', 'list', '--format=json']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            packages = json.loads(result.stdout)
            return [pkg['name'] for pkg in packages]
        except Exception as e:
            print(f"✗ Error listing packages: {str(e)}")
            return []
    
    @staticmethod
    def show_info(package_name: str) -> dict:
        """Show information about a package"""
        import subprocess
        import sys
        
        try:
            cmd = [sys.executable, '-m', 'pip', 'show', package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = {}
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            return info
        except subprocess.CalledProcessError:
            print(f"✗ Package {package_name} not found")
            return {}
        except Exception as e:
            print(f"✗ Error getting package info: {str(e)}")
            return {}
    
    @staticmethod
    def update_all() -> bool:
        """Update all installed packages"""
        import subprocess
        import sys
        
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', '--upgrade-strategy=eager']
            result = subprocess.run(cmd, capture_output=True, text=True)
            # pip install --upgrade without specific packages updates pip itself
            # For updating all packages, we need to get the list first
            installed = PackageManager.list_installed()
            success = True
            for package in installed:
                if not PackageManager.install(package, upgrade=True):
                    success = False
            return success
        except Exception as e:
            print(f"✗ Error updating packages: {str(e)}")
            return False

# Add PackageManager to globals after class definition
BUILT_IN_GLOBALS['PackageManager'] = PackageManager

class Debugger:
    """Basic debugging utilities"""
    
    @staticmethod
    def log(value, label="DEBUG"):
        """Log a value with a label"""
        print(f"[{label}] {value}")
        return value
    
    @staticmethod
    def inspect(obj, show_type=True, show_methods=False):
        """Inspect an object"""
        result = {}
        if show_type:
            result['type'] = __builtins__['type'](obj).__name__
        
        if hasattr(obj, '__dict__'):
            result['attributes'] = obj.__dict__
        elif __builtins__['isinstance'](obj, __builtins__['dict']):
            result['keys'] = __builtins__['list'](obj.keys())
            result['length'] = __builtins__['len'](obj)
        elif hasattr(obj, '__len__'):
            result['length'] = __builtins__['len'](obj)
        
        if show_methods and hasattr(obj, '__class__'):
            methods = [method for method in __builtins__['dir'](obj) if not method.startswith('_')]
            result['methods'] = methods
        
        print(f"Object inspection: {result}")
        return result
    
    @staticmethod
    def breakpoint():
        """Simple breakpoint - wait for user input"""
        print("🔴 BREAKPOINT: Press Enter to continue...")
        input()
    
    @staticmethod
    def trace_call(func, *args, **kwargs):
        """Trace function calls"""
        print(f"📞 Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            print(f"✅ {func.__name__} returned: {result}")
            return result
        except Exception as e:
            print(f"❌ {func.__name__} raised: {type(e).__name__}: {e}")
            raise
    
    @staticmethod
    def time_execution(func, *args, **kwargs):
        """Time function execution"""
        import time
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            print(f"⏱️  {func.__name__} executed in {duration:.4f} seconds")
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print(f"⏱️  {func.__name__} failed after {duration:.4f} seconds: {e}")
            raise

class Profiler:
    """Basic profiling utilities"""
    
    @staticmethod
    def profile_function(func, *args, **kwargs):
        """Profile a function execution"""
        import cProfile
        import pstats
        import io
        
        pr = cProfile.Profile()
        pr.enable()
        
        try:
            result = func(*args, **kwargs)
            pr.disable()
            
            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
            ps.print_stats()
            profile_output = s.getvalue()
            
            print("📊 Function Profile:")
            print(profile_output)
            return result
        except Exception as e:
            pr.disable()
            print(f"❌ Profiling failed: {e}")
            raise
    
    @staticmethod
    def memory_usage():
        """Get current memory usage"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            print(f"🧠 Memory usage: {memory_mb:.2f} MB")
            return memory_mb
        except ImportError:
            print("⚠️  psutil not available for memory profiling")
            return None
    
    @staticmethod
    def start_memory_trace():
        """Start memory tracing"""
        try:
            import tracemalloc
            tracemalloc.start()
            print("🧠 Memory tracing started")
            return True
        except ImportError:
            print("⚠️  tracemalloc not available")
            return False
    
    @staticmethod
    def stop_memory_trace():
        """Stop memory tracing and show top memory users"""
        try:
            import tracemalloc
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            current_mb = current / 1024 / 1024
            peak_mb = peak / 1024 / 1024
            
            print(f"🧠 Memory trace results:")
            print(f"   Current memory: {current_mb:.2f} MB")
            print(f"   Peak memory: {peak_mb:.2f} MB")
            
            return {'current': current_mb, 'peak': peak_mb}
        except ImportError:
            print("⚠️  tracemalloc not available")
            return None

# Add development tools to globals
BUILT_IN_GLOBALS['Debugger'] = Debugger
BUILT_IN_GLOBALS['Profiler'] = Profiler

class Test:
    """Simple testing framework"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
    
    def assert_equal(self, actual, expected, message=""):
        """Assert two values are equal"""
        self.tests_run += 1
        if actual == expected:
            self.tests_passed += 1
            print(f"✓ PASS: {message}")
        else:
            self.tests_failed += 1
            print(f"✗ FAIL: {message} - Expected {expected}, got {actual}")
    
    def assert_true(self, condition, message=""):
        """Assert condition is true"""
        self.assert_equal(condition, True, message)
    
    def assert_false(self, condition, message=""):
        """Assert condition is false"""
        self.assert_equal(condition, False, message)
    
    def assert_raises(self, exception_type, func, message=""):
        """Assert that function raises specific exception"""
        self.tests_run += 1
        try:
            func()
            self.tests_failed += 1
            print(f"✗ FAIL: {message} - Expected {exception_type.__name__} but no exception raised")
        except exception_type:
            self.tests_passed += 1
            print(f"✓ PASS: {message}")
        except Exception as e:
            self.tests_failed += 1
            print(f"✗ FAIL: {message} - Expected {exception_type.__name__} but got {type(e).__name__}")
    
    def run(self):
        """Run all tests and print summary"""
        print(f"\nTest Results: {self.tests_passed}/{self.tests_run} passed, {self.tests_failed} failed")
        return self.tests_failed == 0
