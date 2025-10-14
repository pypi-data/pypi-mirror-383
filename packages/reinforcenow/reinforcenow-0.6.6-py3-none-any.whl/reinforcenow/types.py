"""
Type definitions for the reward and generation systems.

Users decorate their functions with @reward_function or @generation to mark them
for automatic detection and execution.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, Callable, Awaitable, Union, Any, Optional


@dataclass
class Sample:
    """
    Sample data structure for RLHF training.

    This matches the slime package's Sample implementation exactly.
    """

    index: Optional[int] = None

    # Prompt
    prompt: Union[str, list[dict[str, str]]] = ""
    tokens: list[int] = field(default_factory=list)

    # Response
    response: str = ""
    response_length: int = 0
    label: Optional[str] = None
    reward: Optional[Union[float, dict[str, Any]]] = None
    loss_mask: Optional[list[int]] = None
    weight_versions: list[str] = field(default_factory=list)
    rollout_log_probs: Optional[list[float]] = None  # Log probabilities from rollout engine

    class Status(Enum):
        PENDING = "pending"
        COMPLETED = "completed"
        TRUNCATED = "truncated"
        ABORTED = "aborted"

    status: "Sample.Status" = Status.PENDING
    metadata: dict = field(default_factory=dict)
    # metadata used during training, e.g., what loss to use for this sample.
    train_metadata: Optional[dict] = None

    def to_dict(self):
        """Convert Sample to dictionary with status as string value."""
        value = self.__dict__.copy()
        value["status"] = self.status.value
        return value

    @staticmethod
    def from_dict(data: dict) -> "Sample":
        """Create Sample from dictionary, converting status string to enum."""
        data["status"] = Sample.Status(data["status"])
        return Sample(**data)

    def get_reward_value(self, args) -> float:
        """Get the reward value, optionally extracting a specific key from reward dict."""
        return self.reward if not args.reward_key else self.reward[args.reward_key]


class RewardFunction(Protocol):
    """
    Protocol for reward functions.

    Reward functions must:
    - Be async functions
    - Accept (args, sample: Sample, **kwargs) OR (args, code: str, **kwargs)
    - Return float (1.0 for pass, 0.0 for fail)
    - Have __reward_function__ = True attribute
    """
    __reward_function__: bool
    __name__: str

    def __call__(
        self,
        args,
        input: Union[Sample, str],
        **kwargs
    ) -> Awaitable[float]:
        ...


class RewardExecutor(Protocol):
    """
    Protocol for reward executor functions.

    The executor is the entry point called by slime.
    It must:
    - Be an async function
    - Accept (args, sample: Sample, **kwargs)
    - Return dict with 'score' and 'pred'
    - Have __reward_executor__ = True attribute
    """
    __reward_executor__: bool
    __name__: str

    def __call__(
        self,
        args,
        sample: Sample,
        **kwargs
    ) -> Awaitable[dict]:
        ...


def reward_function(func: Callable) -> Callable:
    """
    Decorator to mark a function as a reward function.

    Usage:
        @reward_function
        async def code_brackets(args, sample: Sample, **kwargs) -> float:
            return 1.0 if check_passed else 0.0
    """
    func.__reward_function__ = True
    return func


def reward_executor(func: Callable) -> Callable:
    """
    Decorator to mark a function as the reward executor.

    Usage:
        @reward_executor
        async def custom_executor(args, sample: Sample, **kwargs) -> dict:
            # Your custom execution logic
            return {"score": total_reward, "pred": breakdown}

    If not defined by user, a default executor is automatically provided.
    """
    func.__reward_executor__ = True
    return func


class GenerationFunction(Protocol):
    """
    Protocol for generation functions.

    Generation functions must:
    - Be async functions
    - Accept (args, sample: Sample, sampling_params: dict, state: Any, **kwargs)
    - Return Sample (updated with response, tokens, and status)
    - Have __generation__ = True attribute
    """
    __generation__: bool
    __name__: str

    def __call__(
        self,
        args,
        sample: Sample,
        sampling_params: dict[str, Any],
        state: Optional[Any] = None,
        **kwargs
    ) -> Awaitable[Sample]:
        ...


def generation(func: Callable) -> Callable:
    """
    Decorator to mark a function as a generation function.

    Usage:
        @generation
        async def custom_generate(args, sample: Sample, sampling_params, state) -> Sample:
            # Your custom generation logic
            # Update sample with response, tokens, status
            return sample
    """
    func.__generation__ = True
    return func
