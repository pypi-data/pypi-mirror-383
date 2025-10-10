"""
Internal WebSocket handler for DynamoGuard streaming.

This module contains the low-level WebSocket communication handler
that is used internally by the DynamoGuardStreamingClient.
"""

import json
import logging
import threading
from typing import List

import websocket

logger = logging.getLogger("dynamoguard_streaming")
logger.setLevel("INFO")


class _DynamoGuardAnalyzeStreamingHandler:
    """
    Internal WebSocket handler for DynamoGuard analyze streaming.
    This class handles the low-level WebSocket communication for analyze streaming and is not exposed to users.
    """

    def __init__(self, ws_api_url: str, dynamoai_api_key: str):
        self.ws_api_url = ws_api_url
        self.dynamoai_api_key = dynamoai_api_key
        self.ws = None
        self.last_analysis_result = None  # Latest analysis result
        self.lock = threading.Lock()
        self.connected = False
        self.authorized = False
        self.session_active = False
        self.connection_ready = threading.Event()
        self.session_ready = threading.Event()

    def _send_ws_msg(self, event: str, data: dict):
        """Send a message to the WebSocket server"""
        if not self.connected or not self.ws:
            raise ConnectionError("WebSocket is not connected")

        msg = json.dumps({"event": event, "data": data})
        try:
            self.ws.send(msg)
        except websocket.WebSocketConnectionClosedException as exc:
            self.connected = False
            raise ConnectionError("WebSocket connection was closed") from exc

    def _on_message(self, _ws, message):
        """Handle incoming WebSocket messages"""
        try:
            response = json.loads(message)
            logger.debug("Received: %s", response)

            event = response["event"]
            data = response.get("data", {})

            if event == "client-info":
                # Authorization successful
                self.authorized = True
                self.connection_ready.set()
                logger.info("Authorized successfully")

            elif event == "session_start":
                # Session started successfully
                self.session_active = True
                self.session_ready.set()
                logger.info("Session started successfully")

            elif event == "session_end":
                # Session ended
                self.session_active = False
                logger.info("Session ended")

            elif event == "analyze_result":
                # Handle analysis results
                with self.lock:
                    self.last_analysis_result = data
                    logger.debug("Received batched analysis result: %s", data)
            elif event == "session_reset":
                logger.debug("Session reset")
            elif event == "error":
                # Handle errors
                logger.error("Server error: %s", data)
                if "auth" in data.get("message", "").lower():
                    self.authorized = False
                    self.connection_ready.set()  # Unblock waiting threads
                elif "session" in data.get("message", "").lower():
                    self.session_active = False
                    self.session_ready.set()  # Unblock waiting threads

            else:
                # Log other events
                logger.info("Received event: %s", response)

        except json.JSONDecodeError as e:
            logger.error("Failed to parse message: %s", e)

    def _on_error(self, _ws, error):
        """Handle WebSocket errors"""
        logger.error("WebSocket error: %s", error)
        self.connected = False
        self.connection_ready.set()  # Unblock waiting threads

    def _on_close(self, _ws, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        logger.info("WebSocket closed: %s - %s", close_status_code, close_msg)
        self.session_active = False
        self.connected = False
        self.authorized = False
        self.connection_ready.set()  # Unblock waiting threads
        self.session_ready.set()  # Unblock waiting threads

    def _on_open(self, _ws):
        """Handle WebSocket connection open"""
        logger.info("WebSocket connection opened")
        self.connected = True
        # Authorize immediately after connection
        self._send_ws_msg("auth", {"token": self.dynamoai_api_key})

    def create_connection(self) -> websocket.WebSocketApp:
        """Create and return a WebSocket connection"""
        ws_url = f"{self.ws_api_url}/v1/moderation/stream/analyze"

        if ws_url.startswith("http://"):
            ws_url = ws_url.replace("http://", "ws://")
        elif ws_url.startswith("https://"):
            ws_url = ws_url.replace("https://", "wss://")
        logger.info("Connecting to WebSocket URL: %s", ws_url)
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        return self.ws

    def wait_for_connection(self, timeout: float = 10.0) -> bool:
        """Wait for connection and authorization to complete"""
        if self.connection_ready.wait(timeout):
            return self.authorized
        return False

    def start_session(
        self,
        input_prompt: str,
        policy_ids: List[str],
        model_id: str,
        response_token_buffer_length: int,
    ):
        """Start a new analysis session with the given input prompt"""
        if not self.connected or not self.authorized:
            raise ConnectionError("WebSocket is not connected or not authorized")

        # Reset session ready event
        self.session_ready.clear()

        self._send_ws_msg(
            "start",
            {
                "messages": [{"role": "user", "content": input_prompt}],
                "policyIds": policy_ids,
                "modelId": model_id,
                "responseTokenBufferLength": response_token_buffer_length,
            },
        )

        # Wait for session to start
        if not self.session_ready.wait(5.0):
            raise TimeoutError("Session start timeout")

    def send_chunk_for_analysis(self, output_chunk: str):
        """Send a chunk for analysis without waiting for response"""
        if not self.connected:
            logger.warning("WebSocket not connected, skipping chunk analysis")
            return

        # Send analyze event - server will batch this with other chunks
        try:
            self._send_ws_msg("analyze", {"text": output_chunk})
            logger.debug("Sent chunk for analysis: %s", output_chunk)
        except ConnectionError as e:
            logger.error("Failed to send chunk for analysis: %s", e)

    def get_latest_analysis_result(self) -> dict | None:
        """Get the latest analysis result if available"""
        with self.lock:
            if self.last_analysis_result:
                result = self.last_analysis_result
                self.last_analysis_result = None  # Clear after reading
                return result
            return None

    def end_session(self):
        """End the current analysis session"""
        if self.connected and self.session_active:
            try:
                self._send_ws_msg("end", {})
                # Don't wait for session_end event - just mark as inactive
                self.session_active = False
            except ConnectionError as e:
                logger.warning("Error ending session: %s", e)
        self.session_active = False

    def close(self):
        """Close the WebSocket connection"""
        if self.ws:
            self.ws.close()
