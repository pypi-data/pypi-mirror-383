"""Smart model switching for rate limit handling and fallback strategies."""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from rich.console import Console

console = Console()


class ModelTier(Enum):
    """Model performance/resource tiers."""
    PREMIUM = "premium"      # High-performance, high rate limits
    STANDARD = "standard"    # Balanced performance and limits
    BASIC = "basic"          # Lower performance, more generous limits
    FALLBACK = "fallback"    # Minimal resource usage, highest availability


@dataclass
class ModelInfo:
    """Information about a model and its capabilities."""
    name: str
    tier: ModelTier
    backend: str
    context_length: int
    rate_limit_friendly: bool = False
    cost_efficiency: float = 1.0  # Lower is more cost efficient


class ModelSwitchingStrategy:
    """Intelligent model switching strategy for rate limit handling."""
    
    def __init__(self):
        # Define model hierarchies for each backend
        self.model_hierarchies: Dict[str, List[ModelInfo]] = {
            "groq": [
                # Premium tier - high performance but may hit rate limits faster
                ModelInfo("llama-3.1-70b-versatile", ModelTier.PREMIUM, "groq", 131072, False, 3.0),
                ModelInfo("llama-3.3-70b-versatile", ModelTier.PREMIUM, "groq", 131072, False, 3.0),
                ModelInfo("llama3-70b-8192", ModelTier.PREMIUM, "groq", 8192, False, 2.5),
                
                # Standard tier - good performance, moderate limits
                ModelInfo("llama-3.1-8b-instant", ModelTier.STANDARD, "groq", 131072, True, 1.5),
                ModelInfo("llama3-8b-8192", ModelTier.STANDARD, "groq", 8192, True, 1.2),
                ModelInfo("mixtral-8x7b-32768", ModelTier.STANDARD, "groq", 32768, True, 1.8),
                
                # Basic tier - faster, more rate-limit friendly
                ModelInfo("gemma-7b-it", ModelTier.BASIC, "groq", 8192, True, 1.0),
                ModelInfo("gemma2-9b-it", ModelTier.BASIC, "groq", 8192, True, 1.0),
            ],
            "openai": [
                # Premium tier
                ModelInfo("gpt-4-turbo", ModelTier.PREMIUM, "openai", 128000, False, 4.0),
                ModelInfo("gpt-4", ModelTier.PREMIUM, "openai", 8192, False, 3.5),
                
                # Standard tier
                ModelInfo("gpt-3.5-turbo", ModelTier.STANDARD, "openai", 4096, True, 1.0),
                ModelInfo("gpt-3.5-turbo-16k", ModelTier.STANDARD, "openai", 16384, True, 1.2),
            ],
            "bedrock": [
                # Premium tier
                ModelInfo("anthropic.claude-3-sonnet-20240229-v1:0", ModelTier.PREMIUM, "bedrock", 200000, False, 3.0),
                ModelInfo("anthropic.claude-v2:1", ModelTier.PREMIUM, "bedrock", 100000, False, 2.5),
                
                # Standard tier
                ModelInfo("anthropic.claude-instant-v1", ModelTier.STANDARD, "bedrock", 100000, True, 1.5),
                
                # Basic tier
                ModelInfo("amazon.titan-text-express-v1", ModelTier.BASIC, "bedrock", 8000, True, 1.0),
            ],
            "ollama": [
                # All local models are rate-limit friendly
                ModelInfo("llama2", ModelTier.STANDARD, "ollama", 4096, True, 0.0),
                ModelInfo("mistral", ModelTier.STANDARD, "ollama", 8192, True, 0.0),
                ModelInfo("gemma:7b", ModelTier.BASIC, "ollama", 8192, True, 0.0),
            ]
        }
        
        # Cross-backend fallback preferences (if available)
        self.cross_backend_fallbacks = [
            "ollama",    # Local models first - no rate limits
            "groq",      # Fast and generous free tier
            "openai",    # Reliable but may have stricter limits
            "bedrock",   # Enterprise option
        ]
    
    def get_model_info(self, model_name: str, backend_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model."""
        if backend_name in self.model_hierarchies:
            for model in self.model_hierarchies[backend_name]:
                if model.name == model_name:
                    return model
        return None
    
    def get_fallback_models(self, current_model: str, current_backend: str, 
                           available_backends: List[str]) -> List[Tuple[str, str]]:
        """
        Get fallback models in priority order.
        
        Returns:
            List of (model_name, backend_name) tuples in fallback priority order
        """
        fallbacks = []
        current_model_info = self.get_model_info(current_model, current_backend)
        
        # First try lower-tier models in the same backend
        if current_backend in self.model_hierarchies:
            current_tier = current_model_info.tier if current_model_info else ModelTier.PREMIUM
            
            for model in self.model_hierarchies[current_backend]:
                if (model.name != current_model and 
                    model.rate_limit_friendly and
                    self._is_lower_tier(model.tier, current_tier)):
                    fallbacks.append((model.name, current_backend))
        
        # Then try other backends with rate-limit friendly models
        for backend in self.cross_backend_fallbacks:
            if backend in available_backends and backend != current_backend:
                # Get the most rate-limit friendly model from this backend
                if backend in self.model_hierarchies:
                    rate_friendly_models = [
                        m for m in self.model_hierarchies[backend] 
                        if m.rate_limit_friendly
                    ]
                    if rate_friendly_models:
                        # Sort by tier (basic first) and cost efficiency
                        rate_friendly_models.sort(
                            key=lambda m: (m.tier.value, m.cost_efficiency)
                        )
                        fallbacks.append((rate_friendly_models[0].name, backend))
        
        return fallbacks
    
    def _is_lower_tier(self, tier1: ModelTier, tier2: ModelTier) -> bool:
        """Check if tier1 is a lower resource tier than tier2."""
        tier_order = {
            ModelTier.FALLBACK: 0,
            ModelTier.BASIC: 1, 
            ModelTier.STANDARD: 2,
            ModelTier.PREMIUM: 3
        }
        return tier_order.get(tier1, 0) < tier_order.get(tier2, 3)
    
    def suggest_model_for_task(self, task_complexity: str, backend: str) -> Optional[str]:
        """
        Suggest an appropriate model for a given task complexity.
        
        Args:
            task_complexity: 'simple', 'medium', 'complex'
            backend: Backend name
        
        Returns:
            Recommended model name
        """
        if backend not in self.model_hierarchies:
            return None
        
        models = self.model_hierarchies[backend]
        
        if task_complexity == "simple":
            # Use basic tier models for simple tasks
            basic_models = [m for m in models if m.tier == ModelTier.BASIC]
            if basic_models:
                return min(basic_models, key=lambda m: m.cost_efficiency).name
        elif task_complexity == "complex":
            # Use premium models for complex tasks
            premium_models = [m for m in models if m.tier == ModelTier.PREMIUM]
            if premium_models:
                return premium_models[0].name
        
        # Default to standard tier
        standard_models = [m for m in models if m.tier == ModelTier.STANDARD]
        if standard_models:
            return standard_models[0].name
        
        return models[0].name if models else None
    
    def get_available_models_by_tier(self, backend: str) -> Dict[ModelTier, List[str]]:
        """Get models grouped by tier for a backend."""
        if backend not in self.model_hierarchies:
            return {}
        
        by_tier: Dict[ModelTier, List[str]] = {}
        for model in self.model_hierarchies[backend]:
            if model.tier not in by_tier:
                by_tier[model.tier] = []
            by_tier[model.tier].append(model.name)
        
        return by_tier
    
    def explain_model_switch(self, old_model: str, new_model: str, 
                           old_backend: str, new_backend: str, reason: str) -> str:
        """Generate user-friendly explanation for model switch."""
        old_info = self.get_model_info(old_model, old_backend)
        new_info = self.get_model_info(new_model, new_backend)
        
        explanation = f"🔄 Switching from {old_model}"
        if old_backend != new_backend:
            explanation += f" ({old_backend})"
        
        explanation += f" to {new_model}"
        if old_backend != new_backend:
            explanation += f" ({new_backend})"
        
        explanation += f"\n   Reason: {reason}"
        
        if new_info and new_info.rate_limit_friendly:
            explanation += "\n   ✅ New model is more rate-limit friendly"
        
        if old_info and new_info:
            if new_info.cost_efficiency < old_info.cost_efficiency:
                explanation += "\n   💰 New model is more cost-effective"
        
        return explanation


# Global instance
model_switcher = ModelSwitchingStrategy()