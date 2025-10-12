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

import subprocess
import json
from typing import List, Dict, Any, Optional
from pathlib import Path


class PyrightIntegration:
    """Integration with Pyright type checker"""
    
    def __init__(self):
        self.pyright_available = self._check_pyright_available()
    
    def _check_pyright_available(self) -> bool:
        """Check if Pyright is available"""
        try:
            subprocess.run(['pyright', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def check_python_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Run Pyright on a Python file"""
        if not self.pyright_available:
            return None
        
        try:
            result = subprocess.run(
                ['pyright', '--outputjson', str(file_path)],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.stdout:
                return json.loads(result.stdout)
            
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            pass
        
        return None