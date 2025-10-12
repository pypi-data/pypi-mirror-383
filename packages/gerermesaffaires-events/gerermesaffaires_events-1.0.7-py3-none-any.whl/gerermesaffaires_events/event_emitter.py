from pyee.base import EventEmitter as BaseEventEmitter

from .server import Server


class EventEmitter(BaseEventEmitter):
    """Event emitter for GererMesAffaires webhook events.

    Example:

    ```python
    emitter = EventEmitter(signature="secret")

    @emitter.on("ping")
    def handle_ping(data):
        print(f"Received ping event: {data}")
    ```
    """

    def __init__(self, signature: str, endpoint: str = "/gerermesaffaires/events") -> None:
        """Initialize the event emitter with webhook configuration."""
        super().__init__()
        self._server = Server(signature, endpoint, self)

    @property
    def app(self) -> Server:
        """Get the ASGI application for webhook handling.

        Example:

        ```python
        import uvicorn

        emitter = EventEmitter("secret", "/gerermesaffaires/events")
        app = emitter.app

        if __name__ == "__main__":
            uvicorn.run(app, host="127.0.0.1", port=8000)
        ```
        """
        return self._server.app
