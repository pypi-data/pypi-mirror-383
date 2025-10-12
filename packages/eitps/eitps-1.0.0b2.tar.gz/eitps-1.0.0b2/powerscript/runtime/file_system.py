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

from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import os
import json
import csv
import tempfile
import shutil
import glob
from abc import ABC, abstractmethod


class FileError(Exception):
    """Exception raised for file operations"""
    pass


class FileSystem:
    """PowerScript FileSystem API - Provides all file operations"""
    
    @staticmethod
    def read_text(path: str, encoding: str = 'utf-8') -> str:
        """Read entire file as text"""
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            raise FileError(f"Failed to read file '{path}': {e}")
    
    @staticmethod
    def write_text(path: str, content: str, encoding: str = 'utf-8') -> None:
        """Write text to file"""
        try:
            # Create directory if it doesn't exist
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
        except Exception as e:
            raise FileError(f"Failed to write file '{path}': {e}")
    
    @staticmethod
    def append_text(path: str, content: str, encoding: str = 'utf-8') -> None:
        """Append text to file"""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'a', encoding=encoding) as f:
                f.write(content)
        except Exception as e:
            raise FileError(f"Failed to append to file '{path}': {e}")
    
    @staticmethod
    def read_lines(path: str, encoding: str = 'utf-8') -> List[str]:
        """Read file as list of lines"""
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.readlines()
        except Exception as e:
            raise FileError(f"Failed to read lines from '{path}': {e}")
    
    @staticmethod
    def write_lines(path: str, lines: List[str], encoding: str = 'utf-8') -> None:
        """Write list of lines to file"""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding=encoding) as f:
                f.writelines(lines)
        except Exception as e:
            raise FileError(f"Failed to write lines to '{path}': {e}")
    
    @staticmethod
    def read_bytes(path: str) -> bytes:
        """Read file as bytes"""
        try:
            with open(path, 'rb') as f:
                return f.read()
        except Exception as e:
            raise FileError(f"Failed to read bytes from '{path}': {e}")
    
    @staticmethod
    def write_bytes(path: str, data: bytes) -> None:
        """Write bytes to file"""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'wb') as f:
                f.write(data)
        except Exception as e:
            raise FileError(f"Failed to write bytes to '{path}': {e}")
    
    @staticmethod
    def exists(path: str) -> bool:
        """Check if file or directory exists"""
        return Path(path).exists()
    
    @staticmethod
    def is_file(path: str) -> bool:
        """Check if path is a file"""
        return Path(path).is_file()
    
    @staticmethod
    def is_directory(path: str) -> bool:
        """Check if path is a directory"""
        return Path(path).is_dir()
    
    @staticmethod
    def get_size(path: str) -> int:
        """Get file size in bytes"""
        try:
            return Path(path).stat().st_size
        except Exception as e:
            raise FileError(f"Failed to get size of '{path}': {e}")
    
    @staticmethod
    def get_modified_time(path: str) -> float:
        """Get last modified time as timestamp"""
        try:
            return Path(path).stat().st_mtime
        except Exception as e:
            raise FileError(f"Failed to get modified time of '{path}': {e}")
    
    @staticmethod
    def delete_file(path: str) -> None:
        """Delete a file"""
        try:
            Path(path).unlink()
        except Exception as e:
            raise FileError(f"Failed to delete file '{path}': {e}")
    
    @staticmethod
    def copy_file(src: str, dst: str) -> None:
        """Copy file from source to destination"""
        try:
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        except Exception as e:
            raise FileError(f"Failed to copy '{src}' to '{dst}': {e}")
    
    @staticmethod
    def move_file(src: str, dst: str) -> None:
        """Move/rename file"""
        try:
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dst)
        except Exception as e:
            raise FileError(f"Failed to move '{src}' to '{dst}': {e}")
    
    @staticmethod
    def create_directory(path: str) -> None:
        """Create directory (and parent directories)"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise FileError(f"Failed to create directory '{path}': {e}")
    
    @staticmethod
    def delete_directory(path: str, recursive: bool = False) -> None:
        """Delete directory"""
        try:
            if recursive:
                shutil.rmtree(path)
            else:
                Path(path).rmdir()
        except Exception as e:
            raise FileError(f"Failed to delete directory '{path}': {e}")
    
    @staticmethod
    def list_directory(path: str) -> List[str]:
        """List contents of directory"""
        try:
            return [str(p.name) for p in Path(path).iterdir()]
        except Exception as e:
            raise FileError(f"Failed to list directory '{path}': {e}")
    
    @staticmethod
    def list_files(path: str, pattern: str = "*") -> List[str]:
        """List files in directory matching pattern"""
        try:
            directory = Path(path)
            return [str(f) for f in directory.glob(pattern) if f.is_file()]
        except Exception as e:
            raise FileError(f"Failed to list files in '{path}': {e}")
    
    @staticmethod
    def list_directories(path: str) -> List[str]:
        """List subdirectories"""
        try:
            directory = Path(path)
            return [str(d) for d in directory.iterdir() if d.is_dir()]
        except Exception as e:
            raise FileError(f"Failed to list directories in '{path}': {e}")
    
    @staticmethod
    def get_absolute_path(path: str) -> str:
        """Get absolute path"""
        return str(Path(path).resolve())
    
    @staticmethod
    def get_parent_directory(path: str) -> str:
        """Get parent directory"""
        return str(Path(path).parent)
    
    @staticmethod
    def get_filename(path: str) -> str:
        """Get filename without directory"""
        return Path(path).name
    
    @staticmethod
    def get_file_extension(path: str) -> str:
        """Get file extension"""
        return Path(path).suffix
    
    @staticmethod
    def get_filename_without_extension(path: str) -> str:
        """Get filename without extension"""
        return Path(path).stem
    
    @staticmethod
    def join_path(*parts: str) -> str:
        """Join path components"""
        return str(Path(*parts))
    
    @staticmethod
    def create_temp_file(suffix: str = "", prefix: str = "tmp") -> str:
        """Create temporary file and return path"""
        try:
            fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            os.close(fd)  # Close file descriptor, just return path
            return path
        except Exception as e:
            raise FileError(f"Failed to create temporary file: {e}")
    
    @staticmethod
    def create_temp_directory(prefix: str = "tmp") -> str:
        """Create temporary directory and return path"""
        try:
            return tempfile.mkdtemp(prefix=prefix)
        except Exception as e:
            raise FileError(f"Failed to create temporary directory: {e}")
    
    @staticmethod
    def get_current_directory() -> str:
        """Get current working directory"""
        return str(Path.cwd())
    
    @staticmethod
    def set_current_directory(path: str) -> None:
        """Set current working directory"""
        try:
            os.chdir(path)
        except Exception as e:
            raise FileError(f"Failed to change directory to '{path}': {e}")


class JSONFile:
    """JSON file operations"""
    
    @staticmethod
    def read(path: str) -> Any:
        """Read JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise FileError(f"Failed to read JSON from '{path}': {e}")
    
    @staticmethod
    def write(path: str, data: Any, indent: int = 2) -> None:
        """Write data to JSON file"""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
        except Exception as e:
            raise FileError(f"Failed to write JSON to '{path}': {e}")


class CSVFile:
    """CSV file operations"""
    
    @staticmethod
    def read(path: str, has_header: bool = True) -> List[Dict[str, str]]:
        """Read CSV file as list of dictionaries"""
        try:
            with open(path, 'r', encoding='utf-8', newline='') as f:
                if has_header:
                    reader = csv.DictReader(f)
                    return list(reader)
                else:
                    reader = csv.reader(f)
                    return [dict(enumerate(row)) for row in reader]
        except Exception as e:
            raise FileError(f"Failed to read CSV from '{path}': {e}")
    
    @staticmethod
    def write(path: str, data: List[Dict[str, Any]], fieldnames: Optional[List[str]] = None) -> None:
        """Write data to CSV file"""
        try:
            if not data:
                return
            
            if fieldnames is None:
                fieldnames = list(data[0].keys())
            
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            raise FileError(f"Failed to write CSV to '{path}': {e}")


class FileStream:
    """File stream for reading/writing files in chunks"""
    
    def __init__(self, path: str, mode: str = 'r', encoding: str = 'utf-8', buffer_size: int = 8192):
        self.path = path
        self.mode = mode
        self.encoding = encoding
        self.buffer_size = buffer_size
        self.file = None
        self.is_open = False
    
    def open(self) -> 'FileStream':
        """Open file stream"""
        try:
            if 'b' in self.mode:
                self.file = open(self.path, self.mode, buffering=self.buffer_size)
            else:
                self.file = open(self.path, self.mode, encoding=self.encoding, buffering=self.buffer_size)
            self.is_open = True
            return self
        except Exception as e:
            raise FileError(f"Failed to open file '{self.path}': {e}")
    
    def close(self) -> None:
        """Close file stream"""
        if self.file and self.is_open:
            self.file.close()
            self.is_open = False
    
    def read(self, size: int = -1) -> Union[str, bytes]:
        """Read from stream"""
        if not self.is_open:
            raise FileError("File stream is not open")
        try:
            return self.file.read(size)
        except Exception as e:
            raise FileError(f"Failed to read from '{self.path}': {e}")
    
    def write(self, data: Union[str, bytes]) -> None:
        """Write to stream"""
        if not self.is_open:
            raise FileError("File stream is not open")
        try:
            self.file.write(data)
        except Exception as e:
            raise FileError(f"Failed to write to '{self.path}': {e}")
    
    def flush(self) -> None:
        """Flush stream buffer"""
        if self.is_open and self.file:
            self.file.flush()
    
    def readline(self) -> Union[str, bytes]:
        """Read one line"""
        if not self.is_open:
            raise FileError("File stream is not open")
        try:
            return self.file.readline()
        except Exception as e:
            raise FileError(f"Failed to read line from '{self.path}': {e}")
    
    def readlines(self) -> List[Union[str, bytes]]:
        """Read all lines"""
        if not self.is_open:
            raise FileError("File stream is not open")
        try:
            return self.file.readlines()
        except Exception as e:
            raise FileError(f"Failed to read lines from '{self.path}': {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self.open()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


class DirectoryWatcher:
    """Watch directory for file changes"""
    
    def __init__(self, path: str):
        self.path = path
        self.callbacks = []
    
    def on_change(self, callback):
        """Add callback for file changes"""
        self.callbacks.append(callback)
    
    def start_watching(self):
        """Start watching directory (requires watchdog library)"""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class Handler(FileSystemEventHandler):
                def __init__(self, callbacks):
                    self.callbacks = callbacks
                
                def on_modified(self, event):
                    if not event.is_directory:
                        for callback in self.callbacks:
                            callback('modified', event.src_path)
                
                def on_created(self, event):
                    if not event.is_directory:
                        for callback in self.callbacks:
                            callback('created', event.src_path)
                
                def on_deleted(self, event):
                    if not event.is_directory:
                        for callback in self.callbacks:
                            callback('deleted', event.src_path)
            
            observer = Observer()
            observer.schedule(Handler(self.callbacks), self.path, recursive=True)
            observer.start()
            return observer
            
        except ImportError:
            raise FileError("Directory watching requires 'watchdog' library: pip install watchdog")
        except Exception as e:
            raise FileError(f"Failed to start directory watcher: {e}")


# Convenience aliases for common operations
read_file = FileSystem.read_text
write_file = FileSystem.write_text
file_exists = FileSystem.exists
create_dir = FileSystem.create_directory
list_files = FileSystem.list_files