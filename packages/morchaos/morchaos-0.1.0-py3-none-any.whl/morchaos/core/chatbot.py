"""HTTP client for local Ollama/Chat-model endpoints."""

import json
import logging
from typing import Optional

# Importing requests lazily to give a clear error message if the package
# is missing.  The wrapper exception keeps the original traceback for
# debugging.
try:
    import requests
except ImportError as e:
    raise ImportError(
        "Required package not installed. Run: pip install requests"
    ) from e

logger = logging.getLogger(__name__)


class Chatbot:
    """Simple HTTP client for local chat model endpoints.

    The class abstracts away the details of HTTP communication
    with an Ollama-compatible model server.  It handles:

    * connection establishment (via a ``requests.Session``)
    * request construction & serialization
    * error handling and retries
    * both streamed and non‑streamed responses
    * simple health‑checks and model enumeration

    The client is intentionally lightweight – it only
    implements the features required for a quick command‑line
    or script‑based interaction.
    """

    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 30):
        """Initialize chatbot client.

        Args:
            base_url: Base URL of the chat model API.
            timeout: Request timeout in seconds.
        """
        # Ensure the base URL does not end with a trailing slash to
        # avoid accidental double slashes when concatenating endpoints.
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # A persistent session reuses TCP connections which
        # dramatically improves throughput for repeated calls.
        self.session = requests.Session()

    def ask(
        self, prompt: str, model: str = "llama3.2:latest", stream: bool = False
    ) -> str:
        """Send a prompt to the chat model and get response.

        This is the primary user‑facing method.  It prepares
        the request payload, issues the POST, and then dispatches
        the response to either a streaming or a regular handler.

        Args:
            prompt: Text prompt to send.
            model: Model name to use (default: llama3.2:latest).
            stream: Whether to use streaming response.

        Returns:
            Response text from the model.

        Raises:
            ConnectionError: If unable to connect to the endpoint.
            ValueError: If the response is invalid or the prompt is empty.
        """
        # Guard against empty prompts – the model would simply
        # return an empty string which is almost never useful.
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        url = f"{self.base_url}/api/generate"
        payload = {"model": model, "prompt": prompt, "stream": stream}

        try:
            logger.info(f"Sending request to {url} with model {model}")
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
            # Raise for HTTP error codes (4xx/5xx) to simplify error
            # handling downstream.
            response.raise_for_status()

            if stream:
                return self._handle_streaming_response(response)
            else:
                return self._handle_json_response(response)

        # The exception hierarchy of ``requests`` is rich; we
        # translate the most common ones into domain‑specific
        # errors to keep the API surface small.
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to {url}: {e}")
            raise ConnectionError(
                f"Cannot connect to chat model at {self.base_url}"
            ) from e
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timed out after {self.timeout}s: {e}")
            raise ConnectionError(
                f"Request timed out after {self.timeout} seconds"
            ) from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise ConnectionError(f"Request failed: {e}") from e

    def _handle_json_response(self, response: requests.Response) -> str:
        """Handle non‑streaming JSON response.

        The Ollama API returns a JSON object containing a
        ``response`` field.  We also provide a fallback for
        older or custom responses that might use ``message``.

        Args:
            response: The raw ``requests.Response`` object.

        Returns:
            The textual answer from the model.

        Raises:
            ValueError: If the JSON is malformed or does not
            contain expected keys.
        """
        try:
            data = response.json()
            if "response" in data:
                return str(data["response"])
            elif "message" in data:
                return str(data["message"])
            else:
                logger.warning(f"Unexpected response format: {data}")
                return str(data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError("Invalid JSON response from chat model") from e

    def _handle_streaming_response(self, response: requests.Response) -> str:
        """Handle streaming response (JSONL format).

        The streaming endpoint emits newline‑delimited JSON
        objects.  Each object may contain a partial ``response``
        value and a ``done`` flag signalling the end of the
        message.  We concatenate all partial responses.

        Args:
            response: The raw ``requests.Response`` object.

        Returns:
            The full concatenated response string.

        Raises:
            ValueError: If a line cannot be parsed as JSON.
        """
        full_response = ""
        try:
            for line in response.iter_lines(decode_unicode=True):
                if line.strip():
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            full_response += data["response"]
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        logger.warning(f"Skipping invalid JSON line: {line}")
                        continue
            return full_response
        except Exception as e:
            logger.error(f"Failed to process streaming response: {e}")
            raise ValueError("Failed to process streaming response") from e

    def health_check(self) -> bool:
        """Check if the chat model endpoint is available.

        The health check simply attempts a GET request to the
        ``/api/tags`` endpoint, which is guaranteed to exist on a
        healthy Ollama server.

        Returns:
            True if endpoint is healthy, False otherwise.
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

    def list_models(self) -> list[str]:
        """List available models.

        The method queries the ``/api/tags`` endpoint and extracts
        the ``name`` field from each model entry.

        Returns:
            List of available model names.
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if "models" in data:
                return [model["name"] for model in data["models"]]
            return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
