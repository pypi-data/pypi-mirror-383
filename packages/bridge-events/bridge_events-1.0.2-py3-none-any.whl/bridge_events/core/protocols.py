from typing import Protocol


class EventEmitterProtocol(Protocol):
    """Protocol defining the interface for event emission.

    This protocol establishes the contract for objects that can emit events,
    ensuring compatibility with different event emitter implementations.
    """

    def emit(self, event: str, *args: object, **kwargs: object) -> bool:
        """Emit an event with the given name and arguments."""
        ...
