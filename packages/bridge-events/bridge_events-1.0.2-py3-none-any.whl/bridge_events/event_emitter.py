from pyee.base import EventEmitter as BaseEventEmitter

from .server import Server


class EventEmitter(BaseEventEmitter):
    """Event emitter for Bridge webhook events.

    Example:

    ```python
    emitter = EventEmitter(signature="secret")

    @emitter.on("item.created")
    def handle_item_created(data):
        print(f"Received item created event: {data}")
    ```
    """

    def __init__(self, signature: str, endpoint: str = "/bridge/events") -> None:
        """Initialize the event emitter with webhook configuration."""
        super().__init__()
        self._server = Server(signature, endpoint, self)

    @property
    def app(self) -> Server:
        """Get the ASGI application for webhook handling.

        Example:

        ```python
        import uvicorn

        emitter = EventEmitter("secret", "/bridge/events")
        app = emitter.app

        if __name__ == "__main__":
            uvicorn.run(app, host="127.0.0.1", port=8000)
        ```
        """
        return self._server.app
