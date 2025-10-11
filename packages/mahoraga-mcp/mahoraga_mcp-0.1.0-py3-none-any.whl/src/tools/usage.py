"""
Usage tool - View usage statistics and costs.
Shows token usage and costs per API key with execution history.
"""

from typing import Dict, Any, Optional
from ..usage_tracker import get_tracker


async def usage(api_key: Optional[str] = None, show_recent: int = 5) -> Dict[str, Any]:
    """
    View usage statistics for Mahoraga executions.

    Args:
        api_key: Specific API key to query (optional - shows all if not provided)
        show_recent: Number of recent executions to show (default: 5)

    Returns:
        Dict with usage statistics and execution history
    """
    tracker = get_tracker()

    if api_key:
        # Get stats for specific API key
        summary = tracker.get_usage_summary(api_key)

        if "error" in summary:
            return {
                "status": "not_found",
                "message": f"ℹ️ {summary['error']}"
            }

        # Get recent executions
        recent = tracker.get_recent_executions(api_key, limit=show_recent)

        # Format response
        total_tokens = summary["total_tokens_in"] + summary["total_tokens_out"]

        return {
            "status": "success",
            "api_key": summary["api_key_masked"],
            "summary": {
                "total_executions": summary["total_executions"],
                "total_tokens": total_tokens,
                "tokens_in": summary["total_tokens_in"],
                "tokens_out": summary["total_tokens_out"],
                "total_cost_usd": f"${summary['total_cost_usd']:.4f}",
                "first_used": summary["first_used"],
                "last_used": summary["last_used"]
            },
            "recent_executions": [
                {
                    "task": exec["task"][:50] + "..." if len(exec["task"]) > 50 else exec["task"],
                    "success": "✓" if exec["success"] else "✗",
                    "cost": f"${exec['cost_usd']:.4f}",
                    "tokens": exec["tokens_in"] + exec["tokens_out"],
                    "duration": f"{exec['duration_seconds']:.1f}s",
                    "timestamp": exec["timestamp"]
                }
                for exec in recent
            ],
            "message": f"📊 Usage stats for {summary['api_key_masked']}: {summary['total_executions']} executions, ${summary['total_cost_usd']:.4f} total"
        }

    else:
        # Get stats for all API keys
        summary = tracker.get_usage_summary()

        if summary["total_api_keys"] == 0:
            return {
                "status": "empty",
                "message": "ℹ️ No usage data yet. Run some tasks first!"
            }

        return {
            "status": "success",
            "summary": {
                "total_api_keys": summary["total_api_keys"],
                "total_executions": summary["grand_total_executions"],
                "total_cost_usd": f"${summary['grand_total_cost']:.4f}"
            },
            "api_keys": [
                {
                    "api_key": key["api_key_masked"],
                    "executions": key["total_executions"],
                    "cost": f"${key['total_cost_usd']:.4f}",
                    "first_used": key["first_used"],
                    "last_used": key["last_used"]
                }
                for key in summary["api_keys"]
            ],
            "message": f"📊 Total usage across {summary['total_api_keys']} API key(s): {summary['grand_total_executions']} executions, ${summary['grand_total_cost']:.4f}"
        }