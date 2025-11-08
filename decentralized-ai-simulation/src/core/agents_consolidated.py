# Add this BoundedList class to agents.py for backward compatibility
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
        self._total_appended = 0  # Track total items for statistics

    def append(self, item: Any) -> None:
        """Add item to the list, removing oldest if necessary.

        Args:
            item: Item to append to the list
        """
        with self._lock:
            self._data.append(item)
            self._total_appended += 1

    def extend(self, items: List[Any]) -> None:
        """Add multiple items to the list.

        Args:
            items: List of items to add to the list
        """
        with self._lock:
            self._data.extend(items)
            # If we exceed max_size, remove oldest items
            while len(self._data) > self.max_size:
                self._data.popleft()

    def clear(self) -> None:
        """Clear all items from the list."""
        with self._lock:
            self._data.clear()

    def tolist(self) -> List[Any]:
        """Convert to regular list.

        Returns:
            List containing all items in the bounded list
        """
        with self._lock:
            return list(self._data)

    def __len__(self) -> int:
        """Get current length.

        Returns:
            Current number of items in the list
        """
        with self._lock:
            return len(self._data)

    def __getitem__(self, index: int) -> Any:
        """Get item by index.

        Args:
            index: Index of item to retrieve

        Returns:
            Item at the specified index
        """
        with self._lock:
            return self._data[index]

    def __iter__(self) -> Any:
        """Iterate over items in the list.

        Returns:
            Iterator over items in the list
        """
        with self._lock:
            return iter(self._data)

    def __add__(self, other: Union[List[Any], 'BoundedList']) -> List[Any]:
        """Concatenate with another list or BoundedList.

        Args:
            other: List or BoundedList to concatenate with

        Returns:
            Concatenated list
        """
        if isinstance(other, (list, BoundedList)):
            with self._lock:
                # Convert to regular list for concatenation
                self_list = list(self._data)
                if isinstance(other, BoundedList):
                    other_list = list(other._data)
                else:
                    other_list = other
                return self_list + other_list
        return NotImplemented

    def __radd__(self, other: List[Any]) -> List[Any]:
        """Right-side addition for concatenation.

        Args:
            other: List to concatenate on the left side

        Returns:
            Concatenated list with other first
        """
        if isinstance(other, list):
            with self._lock:
                self_list = list(self._data)
                return other + self_list
        return NotImplemented

    def get_memory_usage(self) -> int:
        """Get estimated memory usage in bytes.

        Returns:
            Estimated memory usage in bytes
        """
        with self._lock:
            # Rough estimate: each item + deque overhead
            item_size = sum(len(str(item)) if hasattr(item, '__len__') else 8 for item in self._data)
            return item_size + 64  # Approximate deque overhead

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the bounded list.

        Returns:
            Dictionary containing list statistics
        """
        with self._lock:
            return {
                'current_size': len(self._data),
                'max_size': self.max_size,
                'total_appended': self._total_appended,
                'memory_usage': self.get_memory_usage()
            }

    def is_full(self) -> bool:
        """Check if the list is at maximum capacity.

        Returns:
            True if list is full, False otherwise
        """
        with self._lock:
            return len(self._data) >= self.max_size