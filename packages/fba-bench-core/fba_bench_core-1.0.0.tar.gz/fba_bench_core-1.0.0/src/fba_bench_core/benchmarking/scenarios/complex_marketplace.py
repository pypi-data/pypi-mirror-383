"""Complex marketplace scenario."""

import random
from typing import Any

from pydantic import BaseModel, Field

from .base import BaseScenario


class ComplexMarketplaceConfig(BaseModel):
    """Configuration for complex marketplace scenario."""

    num_products: int = Field(default=10, gt=0, description="Number of products")
    num_orders: int = Field(default=20, gt=0, description="Number of orders")
    max_quantity: int = Field(default=5, gt=0, description="Maximum quantity per order")
    price_variance: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Price variance"
    )
    allow_backorder: bool = Field(default=False, description="Allow backorders")


class ComplexMarketplaceScenario(BaseScenario):
    """
    This class now correctly implements the modern BaseScenario API.
    """

    def __init__(self, params: dict[str, Any] | None = None):
        """
        The constructor now only accepts a `params` dictionary.
        """
        super().__init__(params)
        self.config = ComplexMarketplaceConfig(**(self.params or {}))

    async def run(self, runner: Any, payload: dict[str, Any]) -> dict[str, Any]:
        """
        All scenario logic is now contained within this single method.
        """
        seed = payload.get("seed", 42)
        rng = random.Random(seed)

        # --- 1. Setup Phase (Logic from old `initialize` and `setup_for_agent`) ---
        world_state = self.setup_simulation(rng)

        original_orders = world_state["remaining_orders"][:]
        total_requested = sum(order["quantity"] for order in original_orders)

        # --- 2. Execution Loop (Logic from old `run` and `update_tick`) ---
        for _ in range(self.config.num_orders):
            self.simulate_market_changes(world_state, self.config.price_variance, rng)

            if not world_state["remaining_orders"]:
                continue

            current_order = world_state["remaining_orders"].pop(0)

            # Interact with the agent runner
            agent_input = self.get_percepts_for_agent(world_state, current_order)
            agent_actions = await runner.process(agent_input)
            self.apply_agent_actions(world_state, agent_actions, current_order)

        # --- 3. Evaluation and Results (Logic from old `evaluate_agent_performance`) ---
        final_metrics = self.calculate_final_kpis(world_state, total_requested)

        return {
            "metrics": final_metrics,
            "final_world_state": world_state,
        }

    def setup_simulation(self, rng: random.Random) -> dict[str, Any]:
        config = self.config
        num_products = config.num_products
        catalog: list[dict[str, Any]] = []
        for i in range(num_products):
            base_price = 10.0 + i * 0.5
            price = base_price * (
                1 + rng.uniform(-config.price_variance, config.price_variance)
            )
            catalog.append({"id": i, "price": round(price, 2)})

        orders: list[dict[str, int]] = []
        for _ in range(config.num_orders):
            product_id = rng.randint(0, num_products - 1)
            quantity = rng.randint(1, config.max_quantity)
            orders.append({"product_id": product_id, "quantity": quantity})

        inventory = {i: rng.randint(10, 100) for i in range(num_products)}

        world_state = {
            "inventory": inventory,
            "catalog": catalog,
            "remaining_orders": orders,
            "history": [],
            "total_revenue": 0.0,
            "total_fulfilled": 0,
        }
        return world_state

    def simulate_market_changes(
        self,
        world_state: dict[str, Any],
        volatility: float,
        rng: random.Random,
    ) -> None:
        for product in world_state["catalog"]:
            product["price"] *= 1 + rng.uniform(-volatility, volatility)
            product["price"] = round(product["price"], 2)

    def get_percepts_for_agent(
        self,
        world_state: dict[str, Any],
        current_order: dict[str, int],
    ) -> dict[str, Any]:
        return {
            "type": "process_order",
            "order": current_order,
            "available_inventory": {
                pid: qty for pid, qty in world_state["inventory"].items() if qty > 0
            },
            "catalog": [p.copy() for p in world_state["catalog"]],
        }

    def apply_agent_actions(
        self,
        world_state: dict[str, Any],
        actions: dict[str, Any],
        current_order: dict[str, int],
    ) -> None:
        product_id = current_order["product_id"]
        requested = current_order["quantity"]
        available = world_state["inventory"].get(product_id, 0)

        fulfilled_quantity = min(
            actions.get("fulfilled_quantity", requested), requested
        )

        use_backorder = (
            actions.get("use_backorder", False) and self.config.allow_backorder
        )
        if use_backorder:
            world_state["inventory"][product_id] -= fulfilled_quantity
        else:
            fulfilled_quantity = min(fulfilled_quantity, available)
            world_state["inventory"][product_id] -= fulfilled_quantity

        price = next(
            p["price"] for p in world_state["catalog"] if p["id"] == product_id
        )
        revenue = fulfilled_quantity * price
        world_state["total_revenue"] += revenue
        world_state["total_fulfilled"] += fulfilled_quantity

        world_state["history"].append(
            {
                "order": current_order,
                "actions": actions,
                "fulfilled": fulfilled_quantity,
                "revenue": revenue,
                "price": price,
            }
        )

    def calculate_final_kpis(
        self,
        world_state: dict[str, Any],
        total_requested: int,
    ) -> dict[str, Any]:
        fulfilled_rate = (
            world_state["total_fulfilled"] / total_requested if total_requested else 0.0
        )
        backorder_amount = sum(
            abs(qty) for qty in world_state["inventory"].values() if qty < 0
        )

        return {
            "total_revenue": round(world_state["total_revenue"], 2),
            "fulfilled_rate": round(fulfilled_rate, 4),
            "total_fulfilled": world_state["total_fulfilled"],
            "total_requested": total_requested,
            "backorder_amount": backorder_amount,
        }
