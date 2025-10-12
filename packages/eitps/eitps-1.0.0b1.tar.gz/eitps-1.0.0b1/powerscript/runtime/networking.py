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

Networking module for PowerScript
Provides basic HTTP operations
"""

import requests
from typing import Dict, Any, Optional


class HTTPClient:
    """Simple HTTP client"""
    
    def __init__(self, base_url: str = ""):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """GET request"""
        full_url = self.base_url + url if self.base_url else url
        response = self.session.get(full_url, params=params, headers=headers)
        return {
            "status_code": response.status_code,
            "text": response.text,
            "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None,
            "headers": dict(response.headers)
        }
    
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, 
             json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """POST request"""
        full_url = self.base_url + url if self.base_url else url
        response = self.session.post(full_url, data=data, json=json, headers=headers)
        return {
            "status_code": response.status_code,
            "text": response.text,
            "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None,
            "headers": dict(response.headers)
        }


def create_http_client(base_url: str = "") -> HTTPClient:
    """Create an HTTP client"""
    return HTTPClient(base_url)