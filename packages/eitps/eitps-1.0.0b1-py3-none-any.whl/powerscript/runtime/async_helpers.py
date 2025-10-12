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

import asyncio
import functools
from typing import Any, Awaitable, Callable, List, TypeVar, Union, Coroutine
from concurrent.futures import ThreadPoolExecutor, Future


T = TypeVar('T')


class AsyncHelper:
    """Helper class for async operations"""
    
    @staticmethod
    async def create_task(coro: Coroutine[Any, Any, T]) -> T:
        """Create and run an async task"""
        task = asyncio.create_task(coro)
        return await task
    
    @staticmethod
    async def gather_tasks(*coroutines: Coroutine[Any, Any, Any]) -> List[Any]:
        """Gather multiple async tasks and wait for all to complete"""
        return await asyncio.gather(*coroutines)
    
    @staticmethod
    async def wait_for(coro: Coroutine[Any, Any, T], timeout: float) -> T:
        """Wait for coroutine with timeout"""
        return await asyncio.wait_for(coro, timeout=timeout)
    
    @staticmethod
    async def sleep(seconds: float) -> None:
        """Async sleep"""
        await asyncio.sleep(seconds)
    
    @staticmethod
    def run_sync(coro: Coroutine[Any, Any, T]) -> T:
        """Run async coroutine in sync context"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're already in an async context, can't use run()
                raise RuntimeError("Cannot run sync in async context")
            return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)
    
    @staticmethod
    async def run_in_thread(func: Callable[..., T], *args, **kwargs) -> T:
        """Run sync function in thread pool"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, func, *args, **kwargs)
    
    @staticmethod
    def async_property(func: Callable[[Any], Awaitable[T]]) -> property:
        """Create an async property"""
        
        def sync_wrapper(self):
            coro = func(self)
            if asyncio.iscoroutine(coro):
                return AsyncHelper.run_sync(coro)
            return coro
        
        return property(sync_wrapper)
    
    @staticmethod
    def async_cached_property(func: Callable[[Any], Awaitable[T]]) -> property:
        """Create a cached async property"""
        cache_name = f'_cached_{func.__name__}'
        
        def sync_wrapper(self):
            if hasattr(self, cache_name):
                return getattr(self, cache_name)
            
            coro = func(self)
            if asyncio.iscoroutine(coro):
                result = AsyncHelper.run_sync(coro)
            else:
                result = coro
            
            setattr(self, cache_name, result)
            return result
        
        return property(sync_wrapper)


# Convenience functions
async def create_task(coro: Coroutine[Any, Any, T]) -> T:
    """Create and run an async task"""
    return await AsyncHelper.create_task(coro)


async def gather_tasks(*coroutines: Coroutine[Any, Any, Any]) -> List[Any]:
    """Gather multiple async tasks"""
    return await AsyncHelper.gather_tasks(*coroutines)


async def wait_for(coro: Coroutine[Any, Any, T], timeout: float) -> T:
    """Wait for coroutine with timeout"""
    return await AsyncHelper.wait_for(coro, timeout)


async def sleep(seconds: float) -> None:
    """Async sleep"""
    await AsyncHelper.sleep(seconds)


def run_sync(coro: Coroutine[Any, Any, T]) -> T:
    """Run async coroutine in sync context"""
    return AsyncHelper.run_sync(coro)


async def run_in_thread(func: Callable[..., T], *args, **kwargs) -> T:
    """Run sync function in thread pool"""
    return await AsyncHelper.run_in_thread(func, *args, **kwargs)


def async_property(func: Callable[[Any], Awaitable[T]]) -> property:
    """Decorator for async properties"""
    return AsyncHelper.async_property(func)


def async_cached_property(func: Callable[[Any], Awaitable[T]]) -> property:
    """Decorator for cached async properties"""
    return AsyncHelper.async_cached_property(func)


class AsyncContext:
    """Context manager for async operations"""
    
    def __init__(self):
        self.tasks: List[asyncio.Task] = []
        self._loop = None
    
    async def __aenter__(self):
        self._loop = asyncio.get_event_loop()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cancel all remaining tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for cancellation to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
    
    def create_task(self, coro: Coroutine[Any, Any, T]) -> asyncio.Task[T]:
        """Create a task within this context"""
        task = asyncio.create_task(coro)
        self.tasks.append(task)
        return task
    
    async def gather(self, *coroutines: Coroutine[Any, Any, Any]) -> List[Any]:
        """Gather coroutines within this context"""
        tasks = [self.create_task(coro) for coro in coroutines]
        return await asyncio.gather(*tasks)


class AsyncQueue:
    """Wrapper around asyncio.Queue with additional functionality"""
    
    def __init__(self, maxsize: int = 0):
        self._queue = asyncio.Queue(maxsize=maxsize)
    
    async def put(self, item: T) -> None:
        """Put item in queue"""
        await self._queue.put(item)
    
    async def get(self) -> T:
        """Get item from queue"""
        return await self._queue.get()
    
    def put_nowait(self, item: T) -> None:
        """Put item in queue without waiting"""
        self._queue.put_nowait(item)
    
    def get_nowait(self) -> T:
        """Get item from queue without waiting"""
        return self._queue.get_nowait()
    
    def empty(self) -> bool:
        """Check if queue is empty"""
        return self._queue.empty()
    
    def full(self) -> bool:
        """Check if queue is full"""
        return self._queue.full()
    
    def qsize(self) -> int:
        """Get queue size"""
        return self._queue.qsize()
    
    def task_done(self) -> None:
        """Mark task as done"""
        self._queue.task_done()
    
    async def join(self) -> None:
        """Wait for all tasks to be done"""  
        await self._queue.join()


class AsyncEvent:
    """Wrapper around asyncio.Event"""
    
    def __init__(self):
        self._event = asyncio.Event()
    
    def set(self) -> None:
        """Set the event"""
        self._event.set()
    
    def clear(self) -> None:
        """Clear the event"""
        self._event.clear()
    
    def is_set(self) -> bool:
        """Check if event is set"""
        return self._event.is_set()
    
    async def wait(self) -> None:
        """Wait for event to be set"""
        await self._event.wait()


def async_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying async functions"""
    
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
            
            raise last_exception
        
        return wrapper
    
    return decorator