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

GUI module for PowerScript using Tkinter
Provides basic GUI components
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Callable, Any


class Window:
    """Basic window class"""
    
    def __init__(self, title: str = "PowerScript App", width: int = 400, height: int = 300):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.widgets = []
    
    def add_button(self, text: str, command: Callable[[], Any], x: int = 0, y: int = 0) -> None:
        """Add a button"""
        button = tk.Button(self.root, text=text, command=command)
        button.place(x=x, y=y)
        self.widgets.append(button)
    
    def add_label(self, text: str, x: int = 0, y: int = 0) -> None:
        """Add a label"""
        label = tk.Label(self.root, text=text)
        label.place(x=x, y=y)
        self.widgets.append(label)
    
    def add_entry(self, x: int = 0, y: int = 0) -> tk.Entry:
        """Add an entry field"""
        entry = tk.Entry(self.root)
        entry.place(x=x, y=y)
        self.widgets.append(entry)
        return entry
    
    def show_message(self, title: str, message: str, type_: str = "info") -> None:
        """Show a message box"""
        if type_ == "info":
            messagebox.showinfo(title, message)
        elif type_ == "warning":
            messagebox.showwarning(title, message)
        elif type_ == "error":
            messagebox.showerror(title, message)
    
    def run(self) -> None:
        """Start the GUI event loop"""
        self.root.mainloop()
    
    def close(self) -> None:
        """Close the window"""
        self.root.destroy()


def create_window(title: str = "PowerScript App", width: int = 400, height: int = 300) -> Window:
    """Create a new window"""
    return Window(title, width, height)