"""
ReinforceNow CLI - Command-line interface for ReinforceNow RLHF platform.
"""

# Export types for user convenience
from reinforcenow.types import (
    Sample,
    RewardFunction,
    RewardExecutor,
    GenerationFunction,
    reward_function,
    reward_executor,
    sub_reward_function,
    generation,
)

__all__ = [
    "Sample",
    "RewardFunction",
    "RewardExecutor",
    "GenerationFunction",
    "reward_function",
    "reward_executor",
    "sub_reward_function",
    "generation",
]

__version__ = "0.8.0"
