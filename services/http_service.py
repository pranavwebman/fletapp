import httpx
import json
from typing import Tuple, Dict, Any, Optional

class HTTPResponseResult:
    def __init__(self, success: bool, status_code: int = 0, response_text: str = "", error_message: str = ""):
        self.success = success
        self.status_code = status_code
        self.response_text = response_text
        self.error_message = error_message

    def __repr__(self):
        return f"<HTTPResponseResult success={self.success} code={self.status_code} err='{self.error_message}'>"


class HTTPService:
    @staticmethod
    async def send_request(
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: int = 5
    ) -> HTTPResponseResult:
        """Sends an asynchronous HTTP request with friendly error handling."""
        if not url:
            return HTTPResponseResult(
                success=False,
                error_message="No URL or endpoint specified."
            )

        if not (url.startswith("http://") or url.startswith("https://")):
            url = f"http://{url}"

        method = method.upper()
        if headers is None:
            headers = {}

        # Parse request body if JSON/dict string
        content = None
        if body and body.strip():
            content = body.strip()
            if "Content-Type" not in headers:
                if content.startswith("{") or content.startswith("["):
                    headers["Content-Type"] = "application/json"

        try:
            async with httpx.AsyncClient(timeout=float(timeout), follow_redirects=True) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    content=content
                )

                if 200 <= response.status_code < 300:
                    return HTTPResponseResult(
                        success=True,
                        status_code=response.status_code,
                        response_text=response.text[:1000]  # truncate long responses
                    )
                else:
                    friendly_err = HTTPService._format_status_error(response.status_code, response.text)
                    return HTTPResponseResult(
                        success=False,
                        status_code=response.status_code,
                        response_text=response.text[:500],
                        error_message=friendly_err
                    )

        except httpx.ConnectTimeout:
            return HTTPResponseResult(
                success=False,
                error_message="Could not reach the ESP device. Connection timed out. Ensure your phone and ESP are on the same Wi-Fi network."
            )
        except httpx.ReadTimeout:
            return HTTPResponseResult(
                success=False,
                error_message="ESP device took too long to respond."
            )
        except httpx.ConnectError:
            return HTTPResponseResult(
                success=False,
                error_message="Connection refused. Check that the IP address and port are correct and the ESP HTTP server is running."
            )
        except httpx.HTTPError as ex:
            return HTTPResponseResult(
                success=False,
                error_message=f"HTTP network error: {str(ex)}"
            )
        except Exception as ex:
            return HTTPResponseResult(
                success=False,
                error_message=f"Request failed: {str(ex)}"
            )

    @staticmethod
    def _format_status_error(code: int, response_text: str) -> str:
        if code == 400:
            return f"HTTP 400: Bad Request. The ESP rejected the parameters."
        elif code == 401:
            return f"HTTP 401: Unauthorized. Authentication required."
        elif code == 403:
            return f"HTTP 403: Forbidden access."
        elif code == 404:
            return f"HTTP 404: Endpoint not found on ESP device."
        elif code >= 500:
            return f"HTTP {code}: ESP internal server error."
        else:
            return f"HTTP Error {code} returned by device."
