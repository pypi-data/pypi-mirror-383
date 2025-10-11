"""
Backend API Client for Mahoraga MCP.
Handles all communication with the Mahoraga backend API.
"""

import os
import httpx
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BackendClient:
    """Client for communicating with Mahoraga backend API."""

    def __init__(self):
        # Get backend URL from environment variable, default to localhost for development
        self.base_url = os.getenv("MAHORAGA_BACKEND_URL", "http://localhost:8000")
        self.timeout = 300.0  # 5 minutes for long-running LLM calls
        logger.info(f"🔧 Backend client initialized: URL={self.base_url}")

    async def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Validate mahoraga_api_key and check user credits.

        Args:
            api_key: The mahoraga API key to validate

        Returns:
            Dict with validation result:
            {
                "valid": bool,
                "user": {"email": str, "name": str, "credits": float},
                "openrouter_api_key": str,
                "error": str (if invalid)
            }
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/validate",
                    json={"api_key": api_key}
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "valid": False,
                        "error": f"API error: {response.status_code}"
                    }

        except Exception as e:
            logger.error(f"Failed to validate API key: {e}")
            return {
                "valid": False,
                "error": f"Connection error: {str(e)}"
            }

    async def log_execution(
        self,
        api_key: str,
        execution_id: str,
        task: str,
        device_serial: str,
        status: str,
        tokens: Optional[Dict[str, int]] = None,
        cost: Optional[float] = None,
        error: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        duration_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Log execution completion and usage to backend.

        Args:
            api_key: Mahoraga API key
            execution_id: Unique execution identifier
            task: Task description
            device_serial: Device serial number
            status: "completed", "failed", or "interrupted"
            tokens: Token usage dict
            cost: Execution cost in USD
            error: Error message if failed
            config: Execution configuration (model, temp, vision, etc.)
            duration_seconds: Time taken to complete

        Returns:
            Dict with logging result:
            {
                "logged": bool,
                "credits_deducted": float,
                "new_balance": float,
                "error": str (if failed)
            }
        """
        logger.info(f"📊 Logging execution - Cost: ${cost}, Status: {status}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/execution/complete",
                    json={
                        "api_key": api_key,
                        "execution_id": execution_id,
                        "task": task,
                        "device_serial": device_serial,
                        "status": status,
                        "tokens": tokens,
                        "cost": cost,
                        "error": error,
                        "config": config,
                        "duration_seconds": duration_seconds
                    }
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Failed to log execution: {response.status_code}")
                    return {"logged": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"Failed to log execution: {e}")
            return {"logged": False, "error": str(e)}


# Singleton instance
_backend_client = None


def get_backend_client() -> BackendClient:
    """Get the global backend client instance."""
    global _backend_client
    if _backend_client is None:
        _backend_client = BackendClient()
    return _backend_client