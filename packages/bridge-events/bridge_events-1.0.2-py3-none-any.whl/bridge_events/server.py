import hashlib
import hmac
from json import dumps

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from .core.exceptions import BridgeError
from .core.protocols import EventEmitterProtocol


class Server(Starlette):
    """HTTP server for handling Bridge webhook requests.

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

    def verify_signature(self, signature_header: str, message: str) -> bool:
        """Verify webhook signature using HMAC-SHA256 hash.

        The signature header may contain multiple signatures separated by commas,
        each prefixed with a scheme. This happens when a webhook's secret is updated,
        as the previous secret remains valid for up to 24 hours.
        """

        signature_hash = hmac.new(
            bytes(self._signature, "utf-8"), bytes(message, "utf-8"), hashlib.sha256
        ).hexdigest()

        return signature_hash.upper() in [
            signature.strip().split("=")[1].upper() for signature in signature_header.split(",")
        ]

    async def handle(self, request: Request) -> Response:
        """Handle incoming webhook requests.

        Validates signature and event headers, then emits the event with
        the request payload. Returns appropriate HTTP status codes.
        """

        json = await request.json()

        # Extract and verify signature from request headers
        signature_header = request.headers.get("BridgeApi-Signature")
        message = dumps(json, separators=(",", ":"))
        if signature_header is None or not self.verify_signature(signature_header, message):
            error = BridgeError("Missing or invalid signature header")
            self._emitter.emit("error", error)
            return Response(status_code=401)

        # Extract event type and emit with request payload
        event = json.get("type", None)
        if event is not None:
            self._emitter.emit(event, json)
            return Response(status_code=200)
        else:
            error = BridgeError("Missing event header")
            self._emitter.emit("error", error)
            return Response(status_code=400)
