"""
DynamoGuard Streaming SDK Client

This module provides the main public interface for the DynamoGuard streaming SDK.
"""

import threading
from typing import List

from .streaming_analyze_handler import _DynamoGuardAnalyzeStreamingHandler


class DynamoGuardStreamingClient:
    """
    DynamoGuard Streaming SDK Client

    This is the main public interface for the DynamoGuard streaming SDK.
    It provides a high-level API for real-time content moderation and analysis.

    Usage:
        client = DynamoGuardStreamingClient(
            ws_api_url="https://api.dynamo.ai",
            dynamoai_api_key="your-api-key"
        )

        # Start session (connection is automatically established)
        client.start_session(
            input_prompt="Your input prompt",
            policy_ids=["policy1", "policy2"],
            model_id="model-id"
        )

        # Send chunks for analysis
        client.send_chunk_for_analysis("chunk of text")

        # Get analysis results
        result = client.get_latest_analysis_result()

        # End session
        client.end_session()

        # Close connection
        client.close()
    """

    def __init__(self, ws_api_url: str, dynamoai_api_key: str, connection_timeout: float = 10.0):
        """
        Initialize the DynamoGuard Streaming Client

        Args:
            ws_api_url: The WebSocket API URL for DynamoGuard
            dynamoai_api_key: The API key for authentication
            connection_timeout: Timeout in seconds for connection establishment (default: 10.0)
        """
        self._handler = _DynamoGuardAnalyzeStreamingHandler(ws_api_url, dynamoai_api_key)
        self._ws_thread = None
        self._connected = False

        # Always connect on initialization
        self._connected = self._establish_connection(connection_timeout)

    def _establish_connection(self, timeout: float = 10.0) -> bool:
        """
        Establish WebSocket connection and wait for authorization

        Args:
            timeout: Timeout in seconds for connection establishment

        Returns:
            True if connection and authorization successful, False otherwise
        """
        ws = self._handler.create_connection()

        self._ws_thread = threading.Thread(target=ws.run_forever)
        self._ws_thread.daemon = True
        self._ws_thread.start()

        return self._handler.wait_for_connection(timeout)

    def is_connected(self) -> bool:
        """
        Check if the client is connected and authorized

        Returns:
            True if connected and authorized, False otherwise
        """
        return self._connected

    def start_session(
        self,
        input_prompt: str,
        policy_ids: List[str],
        model_id: str,
        response_token_buffer_length: int,
    ):
        """
        Start a new analysis session

        Args:
            input_prompt: The input prompt for the session
            policy_ids: List of policy IDs to apply for analysis
            model_id: The model ID to use for analysis
            response_token_buffer_length: The number of tokens to buffer for the response
        """
        if not self._connected:
            raise ConnectionError(
                "Client is not connected. Check your API credentials and network connection."
            )

        self._handler.start_session(
            input_prompt, policy_ids, model_id, response_token_buffer_length
        )

    def send_chunk_for_analysis(self, output_chunk: str):
        """
        Send a chunk of text for analysis

        Args:
            output_chunk: The text chunk to analyze
        """
        if not self._connected:
            raise ConnectionError(
                "Client is not connected. Check your API credentials and network connection."
            )

        self._handler.send_chunk_for_analysis(output_chunk)

    def get_latest_analysis_result(self) -> dict | None:
        """
        Get the latest analysis result

        Returns:
            The latest analysis result ("BLOCK", "ALLOW", etc.) or None if no result available
        """
        return self._handler.get_latest_analysis_result()

    def end_session(self):
        """End the current analysis session"""
        self._handler.end_session()

    def close(self):
        """Close the WebSocket connection and cleanup resources"""
        self._handler.close()
        self._connected = False
        if self._ws_thread and self._ws_thread.is_alive():
            # The thread will terminate when the WebSocket closes
            pass
