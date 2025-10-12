import hashlib

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from .core.exceptions import GererMesAffairesError
from .core.protocols import EventEmitterProtocol


class Server(Starlette):
    """HTTP server for handling GererMesAffaires webhook requests.

    This server extends `Starlette` to provide webhook endpoint handling with
    signature verification and automatic event emission. It validates incoming
    requests and forwards verified events to the event emitter.
    """

    def __init__(self, signature: str, endpoint: str, emitter: EventEmitterProtocol) -> None:
        """Initialize the webhook server."""
        super().__init__(routes=[Route(endpoint, self.handle, methods=["POST"])])
        self._signature = signature
        self._emitter = emitter

    @property
    def app(self) -> "Server":
        """Get the server application instance."""
        return self

    def verify_signature(self, signature: str) -> bool:
        """Verify webhook signature using SHA1 hash."""
        signature_hash = f"sha1={hashlib.sha1(self._signature.encode()).hexdigest()}"
        return signature_hash == signature

    async def handle(self, request: Request) -> Response:
        """Handle incoming webhook requests.

        Validates signature and event headers, then emits the event with
        the request payload. Returns appropriate HTTP status codes.
        """

        # Extract and verify signature from request headers
        signature = request.headers.get("X-Gerer-Mes-Affaires-Signature")
        if signature is None or not self.verify_signature(signature):
            error = GererMesAffairesError("Missing or invalid signature header")
            self._emitter.emit("error", error)
            return Response(status_code=403)

        # Extract event type and emit with request payload
        event = request.headers.get("X-Gerer-Mes-Affaires-Event")
        if event is not None:
            self._emitter.emit(event, await request.json())
            return Response(status_code=200)
        else:
            error = GererMesAffairesError("Missing event header")
            self._emitter.emit("error", error)
            return Response(status_code=400)
