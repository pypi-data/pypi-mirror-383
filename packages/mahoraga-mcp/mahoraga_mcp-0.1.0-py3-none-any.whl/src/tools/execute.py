"""
Execute tool - Run automation tasks with live streaming.
Executes tasks using Mahoraga agent with real-time progress updates.
"""

import os
import logging
import time
from typing import Dict, Any, Callable, Optional
from ..state import get_state
from ..usage_tracker import get_tracker
from ..backend_client import get_backend_client


# Setup logging to capture Mahoraga output
logger = logging.getLogger("mahoraga")


async def execute(
    task: str,
    progress_callback: Optional[Callable[[str], None]] = None
) -> Dict[str, Any]:
    """
    Execute an automation task on the connected Android device.

    Args:
        task: Natural language task description
        progress_callback: Optional callback for streaming progress updates

    Returns:
        Dict with execution result and details
    """
    state = get_state()
    backend = get_backend_client()

    # Check prerequisites
    if not state.is_device_connected():
        return {
            "status": "error",
            "message": "❌ No device connected. Please run 'connect' first.",
            "prerequisite": "connect"
        }

    if not state.is_configured():
        return {
            "status": "error",
            "message": "❌ Configuration incomplete. Please run 'configure' with your Mahoraga API key.",
            "prerequisite": "configure"
        }

    if not state.portal_ready:
        return {
            "status": "error",
            "message": "⚠️ Portal accessibility service not ready. Please ensure it's enabled on the device.",
            "prerequisite": "connect"
        }

    # Validate mahoraga API key with backend
    mahoraga_api_key = state.config["api_key"]
    validation_result = await backend.validate_api_key(mahoraga_api_key)

    if not validation_result.get("valid", False):
        error_msg = validation_result.get("error", "Invalid API key")
        return {
            "status": "error",
            "message": f"❌ API Key validation failed: {error_msg}",
            "prerequisite": "configure"
        }

    # Check user credits
    user_info = validation_result.get("user", {})
    credits = user_info.get("credits", 0)

    if credits <= 0:
        return {
            "status": "error",
            "message": f"❌ Insufficient credits. Current balance: ${credits:.2f}. Please add credits at https://mahoraga.app",
            "user": user_info
        }

    # Get OpenRouter API key from backend (backend manages the actual key)
    openrouter_api_key = validation_result.get("openrouter_api_key")

    if not openrouter_api_key:
        return {
            "status": "error",
            "message": "❌ Backend configuration error: OpenRouter API key not available. Please contact support.",
            "prerequisite": "configure"
        }

    def log_progress(message: str):
        """Send progress updates."""
        if progress_callback:
            progress_callback(message)

    # Track execution time
    start_time = time.time()
    execution_id = None

    try:
        # Use OpenRouter API key from backend validation response
        os.environ["OPENROUTER_API_KEY"] = openrouter_api_key

        log_progress(f"✅ API Key validated - Credits: ${credits:.2f}")
        log_progress(f"👤 User: {user_info.get('name', 'Unknown')}")
        log_progress(f"🚀 Starting task: {task}")
        log_progress(f"📱 Device: {state.device_serial}")
        log_progress(f"🧠 Model: {state.config['model']}")

        # Import Mahoraga components
        from mahoraga.agent.mahoraga import MahoragaAgent
        from mahoraga.agent.utils.llm_picker import load_llm
        from mahoraga.tools import AdbTools
        from mahoraga.agent.context.personas import DEFAULT

        # Setup tools
        log_progress("🔧 Initializing device tools...")
        tools = AdbTools(serial=state.device_serial)

        # Setup LLM
        log_progress("🤖 Loading language model...")
        base_llm = load_llm(
            model=state.config["model"],
            temperature=state.config["temperature"]
        )

        # Wrap LLM with usage tracking
        from ..llm_wrapper import UsageTrackingLLM
        llm = UsageTrackingLLM(base_llm, state.config["model"])

        # Setup agent
        log_progress("⚙️ Initializing Mahoraga agent...")
        agent = MahoragaAgent(
            goal=task,
            llm=llm,
            tools=tools,
            personas=[DEFAULT],
            max_steps=state.config["max_steps"],
            vision=state.config["vision"],
            reasoning=state.config["reasoning"],
            reflection=state.config["reflection"],
            debug=state.config["debug"],
            timeout=1000,
            save_trajectories="none"
        )

        # Run agent with event streaming
        log_progress("▶️ Executing task...")
        handler = agent.run()

        step_count = 0
        async for event in handler.stream_events():
            # Parse different event types and send progress
            event_type = type(event).__name__

            if "Thinking" in event_type or "Input" in event_type:
                step_count += 1
                log_progress(f"[STEP {step_count}] 🧠 Thinking...")

            elif "Execution" in event_type:
                log_progress(f"[ACTION] 🔧 Executing action...")

            elif "Result" in event_type:
                if hasattr(event, 'output'):
                    output = str(event.output)[:100]
                    log_progress(f"[RESULT] 💡 {output}")

            elif "Plan" in event_type:
                if hasattr(event, 'tasks') and event.tasks:
                    log_progress(f"[PLAN] 📋 Created {len(event.tasks)} tasks")

            elif "Screenshot" in event_type:
                log_progress(f"[CAPTURE] 📸 Screenshot captured")

            elif "Complete" in event_type or "Finalize" in event_type:
                log_progress(f"[COMPLETE] ✅ Task execution finished")

        # Get final result
        result = await handler

        # Calculate execution duration
        duration = time.time() - start_time

        # Get usage summary from LLM wrapper
        usage_summary = await llm.get_usage_summary()

        # Record usage to tracker (local tracking)
        tracker = get_tracker()
        success = result.get("success", False)
        tracker.record_execution(
            api_key=mahoraga_api_key,
            task=task,
            model=state.config["model"],
            tokens_in=usage_summary["prompt_tokens"],
            tokens_out=usage_summary["completion_tokens"],
            cost_usd=usage_summary["costs"]["total_usd"],
            success=success,
            duration_seconds=duration,
            error=None if success else result.get("reason", "Unknown error")
        )

        # Log execution to backend for credit deduction and tracking
        await backend.log_execution(
            api_key=mahoraga_api_key,
            execution_id=execution_id or f"exec_{int(time.time())}",
            task=task,
            device_serial=state.device_serial,
            status="completed" if success else "failed",
            tokens={
                "prompt": usage_summary["prompt_tokens"],
                "completion": usage_summary["completion_tokens"],
                "total": usage_summary["total_tokens"]
            },
            cost=usage_summary["costs"]["total_usd"],
            error=None if success else result.get("reason", "Unknown error"),
            config={
                "model": state.config["model"],
                "temperature": state.config["temperature"],
                "vision": state.config["vision"],
                "reasoning": state.config["reasoning"],
                "reflection": state.config["reflection"],
                "debug": state.config["debug"]
            },
            duration_seconds=duration
        )

        # Log usage info
        log_progress(f"💰 Usage: {usage_summary['total_tokens']} tokens, ${usage_summary['costs']['total_usd']:.4f}")
        if usage_summary['image_count'] > 0:
            log_progress(f"📸 Images: {usage_summary['image_count']} (${usage_summary['costs']['image_usd']:.4f})")

        # Parse result
        reason = result.get("reason", result.get("output", "No output"))
        steps = result.get("steps", step_count)

        if success:
            log_progress(f"✅ Task completed successfully in {steps} steps")
            return {
                "status": "success",
                "steps_taken": steps,
                "final_message": reason,
                "message": f"✅ Success: {reason}"
            }
        else:
            log_progress(f"❌ Task failed: {reason}")
            return {
                "status": "failed",
                "steps_taken": steps,
                "final_message": reason,
                "message": f"❌ Failed: {reason}"
            }

    except KeyboardInterrupt:
        log_progress("⏹️ Task interrupted by user")
        return {
            "status": "interrupted",
            "message": "⏹️ Task execution interrupted"
        }

    except Exception as e:
        error_msg = str(e)
        log_progress(f"💥 Error: {error_msg}")
        return {
            "status": "error",
            "message": f"💥 Execution error: {error_msg}",
            "error": error_msg
        }