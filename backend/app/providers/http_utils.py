import asyncio
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("exampilot.providers")

# Status codes safe for transient retry
RETRYABLE_STATUS_CODES = {429, 502, 503, 504}
NON_RETRYABLE_STATUS_CODES = {400, 401, 403, 404, 422}

async def execute_provider_request_with_retry(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: float = 45.0,
    max_retries: int = 2
) -> httpx.Response:
    """
    Executes an HTTP request with exponential backoff for safe transient errors (429, 502, 503, 504).
    Immediately raises on non-retryable errors (401, 403, 400).
    """
    last_exception = None
    delay = 1.0

    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method.upper() == "GET":
                    resp = await client.get(url, headers=headers, params=params)
                else:
                    resp = await client.post(url, headers=headers, json=json_data, params=params)

                # If successful or terminal non-retryable error, return immediately
                if resp.status_code == 200 or resp.status_code in NON_RETRYABLE_STATUS_CODES:
                    return resp
                
                # Check if retryable
                if resp.status_code in RETRYABLE_STATUS_CODES:
                    logger.warning(
                        f"Transient provider error ({resp.status_code}) on attempt {attempt + 1}/{max_retries + 1}. Retrying in {delay}s..."
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(delay)
                        delay *= 2.0
                        continue
                
                return resp
        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as exc:
            last_exception = exc
            logger.warning(f"Connection timeout/error on attempt {attempt + 1}/{max_retries + 1}: {str(exc)}")
            if attempt < max_retries:
                await asyncio.sleep(delay)
                delay *= 2.0
                continue
            raise RuntimeError(f"Provider request timed out after {max_retries + 1} attempts: {str(exc)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected provider connection failure: {str(e)}")

    if last_exception:
        raise RuntimeError(f"Provider connection failed after retries: {str(last_exception)}")
    
    raise RuntimeError("Provider request failed after retries.")
