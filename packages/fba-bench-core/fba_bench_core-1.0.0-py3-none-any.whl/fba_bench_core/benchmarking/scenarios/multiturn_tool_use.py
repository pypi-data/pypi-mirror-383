"""Multi-turn tool use scenario."""

import random
from typing import Any

from pydantic import BaseModel, Field

from .base import BaseScenario


class MultiTurnToolUseConfig(BaseModel):
    """Configuration for multi-turn tool use scenario."""

    steps: int = Field(default=5, gt=0, description="Number of steps")
    include_math: bool = Field(default=True, description="Include math operations")
    include_extraction: bool = Field(
        default=True, description="Include data extraction"
    )
    include_transform: bool = Field(
        default=True, description="Include data transformation"
    )


class MultiturnToolUseScenario(BaseScenario):
    """
    Scenario for evaluating agents on multi-turn tool usage across different capabilities.

    Agents must demonstrate effective tool selection and usage over multiple sequential turns,
    handling tasks like mathematical computations, data extraction, and transformations.
    """

    def __init__(self, params: dict[str, Any] | None = None):
        """
        Initialize the multiturn tool use scenario.

        Args:
            params: A dictionary of parameters that configure this scenario.
        """
        super().__init__(params)
        self.config = MultiTurnToolUseConfig(**self.params)

    async def run(self, runner: Any, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Asynchronously executes the multiturn tool use scenario.

        This method orchestrates a sequence of turns where the agent must use appropriate tools
        for tasks involving math, extraction, or transformation based on enabled capabilities.
        State is tracked across turns, and metrics are computed based on success rates.

        Args:
            runner: The agent runner instance, expected to have an async `process` method
                    that takes input data and returns a response dict with 'success' bool
                    and optional 'result' for verification.
            payload: Runtime parameters, including 'seed' for reproducible randomness.

        Returns:
            Dictionary with scenario results, including metrics (success rates per capability),
            final state (success counts, attempts), and interaction history.
        """
        seed = payload.get("seed", 0)
        rng = random.Random(seed)

        # --- 1. Setup Phase ---
        capabilities = self._determine_capabilities()
        state = self._initialize_state(capabilities)

        # --- 2. Execution Loop ---
        for step in range(1, self.config.steps + 1):
            capability = self._choose_capability(capabilities, rng)
            agent_input = self._build_task_input(capability, rng)
            response = await runner.process(agent_input)
            self._record_interaction(state, step, capability, agent_input, response)

        # --- 3. Evaluation ---
        metrics = self._compute_metrics(state, self.config.steps, capabilities)

        return {
            "metrics": metrics,
            "final_state": {
                "successes": state["successes"],
                "total_attempts": state["total_attempts"],
            },
            "interactions": state["interactions"],
        }

    def _determine_capabilities(self) -> list[str]:
        capabilities: list[str] = []
        if self.config.include_math:
            capabilities.append("math")
        if self.config.include_extraction:
            capabilities.append("extraction")
        if self.config.include_transform:
            capabilities.append("transform")
        if not capabilities:
            capabilities.append("basic")
        return capabilities

    def _initialize_state(self, capabilities: list[str]) -> dict[str, Any]:
        return {
            "interactions": [],
            "successes": {capability: 0 for capability in capabilities},
            "total_attempts": {capability: 0 for capability in capabilities},
        }

    def _choose_capability(self, capabilities: list[str], rng: random.Random) -> str:
        return rng.choice(capabilities)

    def _build_task_input(self, capability: str, rng: random.Random) -> dict[str, Any]:
        if capability == "math":
            a, b = rng.randint(1, 100), rng.randint(1, 100)
            return {
                "task": "math",
                "problem": f"Calculate the sum of {a} and {b}.",
                "expected_result": a + b,
            }
        if capability == "extraction":
            value = rng.randint(100, 999)
            return {
                "task": "extraction",
                "text": f"The key value in this document is {value}. Extract it.",
                "expected_result": value,
            }
        if capability == "transform":
            data = [rng.randint(1, 10) for _ in range(5)]
            return {
                "task": "transform",
                "data": data,
                "operation": "sort ascending",
                "expected_result": sorted(data),
            }
        return {
            "task": "basic",
            "query": "Perform a simple tool call to confirm functionality.",
        }

    def _record_interaction(
        self,
        state: dict[str, Any],
        step: int,
        capability: str,
        agent_input: dict[str, Any],
        response: dict[str, Any],
    ) -> None:
        state["interactions"].append(
            {
                "step": step,
                "task_type": capability,
                "input": agent_input,
                "response": response,
            }
        )
        success = response.get("success", False)
        if success:
            state["successes"][capability] += 1
        state["total_attempts"][capability] += 1

    def _compute_metrics(
        self,
        state: dict[str, Any],
        total_steps: int,
        capabilities: list[str],
    ) -> dict[str, Any]:
        overall_attempts = sum(state["total_attempts"].values())
        total_successes = sum(state["successes"].values())
        metrics: dict[str, Any] = {
            "overall_success_rate": (
                total_successes / overall_attempts if overall_attempts else 0.0
            ),
            "steps_completed": total_steps,
        }
        for capability in capabilities:
            attempts = state["total_attempts"][capability]
            metrics[f"{capability}_success_rate"] = (
                state["successes"][capability] / attempts if attempts else 0.0
            )
        return metrics
