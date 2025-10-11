"""
Usage tracking system for Mahoraga MCP.
Tracks API key usage, costs, and execution history.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class ExecutionRecord:
    """Record of a single execution"""
    timestamp: str
    task: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    success: bool
    duration_seconds: float
    error: Optional[str] = None


class UsageTracker:
    """Tracks usage statistics per API key"""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize usage tracker with storage location"""
        if storage_path is None:
            storage_path = os.path.expanduser("~/.mahoraga/usage.json")

        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_data()

    def _load_data(self):
        """Load usage data from disk"""
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def _save_data(self):
        """Save usage data to disk"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def _mask_api_key(self, api_key: str) -> str:
        """Mask API key for display (show first 10 and last 6 chars)"""
        if len(api_key) < 20:
            return api_key[:4] + "..." + api_key[-4:]
        return api_key[:10] + "..." + api_key[-6:]

    def record_execution(
        self,
        api_key: str,
        task: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        cost_usd: float,
        success: bool,
        duration_seconds: float,
        error: Optional[str] = None
    ):
        """Record an execution for an API key"""

        # Initialize API key record if doesn't exist
        if api_key not in self.data:
            self.data[api_key] = {
                "first_used": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat(),
                "total_executions": 0,
                "total_tokens_in": 0,
                "total_tokens_out": 0,
                "total_cost_usd": 0.0,
                "executions": []
            }

        # Update aggregates
        key_data = self.data[api_key]
        key_data["last_used"] = datetime.now().isoformat()
        key_data["total_executions"] += 1
        key_data["total_tokens_in"] += tokens_in
        key_data["total_tokens_out"] += tokens_out
        key_data["total_cost_usd"] += cost_usd

        # Add execution record
        execution = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": cost_usd,
            "success": success,
            "duration_seconds": duration_seconds,
            "error": error
        }

        # Keep only last 100 executions per key
        key_data["executions"].append(execution)
        if len(key_data["executions"]) > 100:
            key_data["executions"] = key_data["executions"][-100:]

        self._save_data()

    def get_usage_summary(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Get usage summary for a specific API key or all keys"""
        if api_key:
            if api_key not in self.data:
                return {
                    "api_key": self._mask_api_key(api_key),
                    "error": "No usage data found for this API key"
                }

            data = self.data[api_key].copy()
            data["api_key_masked"] = self._mask_api_key(api_key)
            return data
        else:
            # Return summary for all API keys
            summaries = []
            for key, data in self.data.items():
                summary = {
                    "api_key_masked": self._mask_api_key(key),
                    "total_executions": data["total_executions"],
                    "total_cost_usd": data["total_cost_usd"],
                    "first_used": data["first_used"],
                    "last_used": data["last_used"]
                }
                summaries.append(summary)

            return {
                "total_api_keys": len(summaries),
                "api_keys": summaries,
                "grand_total_cost": sum(s["total_cost_usd"] for s in summaries),
                "grand_total_executions": sum(s["total_executions"] for s in summaries)
            }

    def get_recent_executions(self, api_key: str, limit: int = 10) -> List[Dict]:
        """Get recent executions for an API key"""
        if api_key not in self.data:
            return []

        executions = self.data[api_key]["executions"]
        return executions[-limit:][::-1]  # Reverse to show most recent first


# Global tracker instance
_tracker = None


def get_tracker() -> UsageTracker:
    """Get the global usage tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker