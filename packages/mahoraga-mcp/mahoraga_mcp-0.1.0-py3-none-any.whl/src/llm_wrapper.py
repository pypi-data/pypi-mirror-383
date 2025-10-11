"""
LLM wrapper for usage tracking.
Wraps llama-index LLM to track exact token usage and image counts.
"""

from typing import Any, List, Optional
import requests
from llama_index.core.llms import ChatMessage


class UsageTrackingLLM:
    """Wraps an LLM to track token and image usage"""

    def __init__(self, base_llm: Any, model_name: str):
        """
        Initialize usage tracking wrapper.

        Args:
            base_llm: The base llama-index LLM to wrap
            model_name: Model name for pricing lookup (e.g., 'anthropic/claude-sonnet-4')
        """
        self.base_llm = base_llm
        self.model_name = model_name

        # Usage accumulators
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.image_count = 0

        # Pricing info (cached after first fetch)
        self._pricing = None

    def _count_images_in_messages(self, messages: List[ChatMessage]) -> int:
        """Count images in chat messages"""
        count = 0
        for msg in messages:
            if hasattr(msg, 'blocks') and msg.blocks:
                # Count ImageBlock instances
                from llama_index.core.base.llms.types import ImageBlock
                count += sum(1 for block in msg.blocks if isinstance(block, ImageBlock))
        return count

    async def _fetch_pricing(self) -> dict:
        """Fetch model pricing from OpenRouter API"""
        if self._pricing is not None:
            return self._pricing

        try:
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                timeout=10
            )
            response.raise_for_status()
            models_data = response.json()

            # Find pricing for our model
            for model in models_data.get('data', []):
                if model['id'] == self.model_name:
                    pricing = model.get('pricing', {})
                    self._pricing = {
                        'prompt': float(pricing.get('prompt', '0')),
                        'completion': float(pricing.get('completion', '0')),
                        'image': float(pricing.get('image', '0'))
                    }
                    return self._pricing

            # Model not found, default to zero
            self._pricing = {'prompt': 0.0, 'completion': 0.0, 'image': 0.0}
            return self._pricing

        except Exception:
            # On error, return zero pricing
            return {'prompt': 0.0, 'completion': 0.0, 'image': 0.0}

    async def achat(self, messages: List[ChatMessage], **kwargs):
        """Chat method with usage tracking"""

        # Count images before sending
        image_count = self._count_images_in_messages(messages)
        self.image_count += image_count

        # Call base LLM
        response = await self.base_llm.achat(messages, **kwargs)

        # Track token usage from response
        if hasattr(response, 'additional_kwargs'):
            kwargs_data = response.additional_kwargs
            self.prompt_tokens += kwargs_data.get('prompt_tokens', 0)
            self.completion_tokens += kwargs_data.get('completion_tokens', 0)

        return response

    def chat(self, messages: List[ChatMessage], **kwargs):
        """Synchronous chat method with usage tracking"""

        # Count images before sending
        image_count = self._count_images_in_messages(messages)
        self.image_count += image_count

        # Call base LLM
        response = self.base_llm.chat(messages, **kwargs)

        # Track token usage from response
        if hasattr(response, 'additional_kwargs'):
            kwargs_data = response.additional_kwargs
            self.prompt_tokens += kwargs_data.get('prompt_tokens', 0)
            self.completion_tokens += kwargs_data.get('completion_tokens', 0)

        return response

    async def get_usage_summary(self) -> dict:
        """Get accumulated usage with cost calculation"""

        # Fetch pricing
        pricing = await self._fetch_pricing()

        # Calculate costs
        prompt_cost = self.prompt_tokens * pricing['prompt']
        completion_cost = self.completion_tokens * pricing['completion']
        image_cost = self.image_count * pricing['image']
        total_cost = prompt_cost + completion_cost + image_cost

        return {
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.prompt_tokens + self.completion_tokens,
            'image_count': self.image_count,
            'pricing': pricing,
            'costs': {
                'prompt_usd': prompt_cost,
                'completion_usd': completion_cost,
                'image_usd': image_cost,
                'total_usd': total_cost
            }
        }

    def reset(self):
        """Reset usage counters"""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.image_count = 0

    # Pass through all other attributes to base LLM
    def __getattr__(self, name):
        return getattr(self.base_llm, name)