"""
BoundedList class for backward compatibility.
Thread-safe bounded list that maintains a maximum size.
"""

from collections import deque
import threading
from typing import Any, Union, List, Dict

class BoundedList:
    """
    Thread-safe bounded list that maintains a maximum size.
    When the list exceeds max_size, oldest items are removed.
    Optimized for memory efficiency and performance.
    """

    def __init__(self, max_size: int = 1000):
        if max_size <= 0:
            raise ValueError("max_size must be positive")

        self.max_size = max_size
        self._data = deque(maxlen=max_size)
        self._lock = threading.Lock()
        self._total_appended = 0

    def append(self, item: Any) -> None:
        """Add item to the list, removing oldest if necessary."""
        with self._lock:
            self._data.append(item)
            self._total_appended += 1

    def extend(self, items: List[Any]) -> None:
        """Add multiple items to the list."""
        with self._lock:
            self._data.extend(items)
            while len(self._data) > self.max_size:
                self._data.popleft()

    def tolist(self) -> List[Any]:
        """Convert to regular list."""
        with self._lock:
            return list(self._data)

    def __len__(self) -> int:
        """Get current length."""
        with self._lock:
            return len(self._data)

    def __iter__(self) -> Any:
        """Iterate over items in the list."""
        with self._lock:
            return iter(self._data)

    def __add__(self, other: Union[List[Any], 'BoundedList']) -> List[Any]:
        """Concatenate with another list or BoundedList."""
        if isinstance(other, (list, BoundedList)):
            with self._lock:
                self_list = list(self._data)
                if isinstance(other, BoundedList):
                    other_list = list(other._data)
                else:
                    other_list = other
                return self_list + other_list
        return NotImplemented

    def __getitem__(self, index: int) -> Any:
        """Get item by index."""
        with self._lock:
            return self._data[index]