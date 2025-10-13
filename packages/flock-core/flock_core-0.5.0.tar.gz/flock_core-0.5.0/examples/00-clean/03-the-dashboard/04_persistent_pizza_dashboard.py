from __future__ import annotations

import asyncio
from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel

from flock.orchestrator import Flock
from flock.registry import flock_type
from flock.store import SQLiteBlackboardStore


@flock_type
class MyDreamPizza(BaseModel):
    pizza_idea: str

@flock_type
class Pizza(BaseModel):
    ingredients: list[str]
    size: str
    crust_type: str
    step_by_step_instructions: list[str]

def build_orchestrator(db_path: Path) -> tuple[Flock, SQLiteBlackboardStore]:
    store = SQLiteBlackboardStore(db_path)
    flock = Flock("openai/gpt-4.1", store=store)
    (
        flock.agent("pizza_master")
        .description("Turns pizza dreams into structured recipes.")
        .consumes(MyDreamPizza)
        .publishes(Pizza)
    )
    return flock, store

async def bake_pizzas(flock: Flock, ideas: Iterable[str]) -> None:
    for idea in ideas:
        artifact = MyDreamPizza(pizza_idea=idea)
        print(f"📨 Publishing idea: {artifact.pizza_idea}")
        await flock.publish(artifact)
    await flock.run_until_idle()

async def show_recent_history(flock: Flock, limit: int = 5) -> None:
    artifacts = await flock.store.list(limit=limit)
    print("\n🗂️  Persisted artifacts:")
    for artifact in artifacts:
        print(f" - {artifact.type} from {artifact.produced_by} @ {artifact.created_at}")

async def main() -> None:
    db_path = Path(".flock/examples/pizza_history.db").resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    flock, store = build_orchestrator(db_path)
    await flock.serve(dashboard=True)
    try:
        await store.ensure_schema()
        print(f"\n✅ History stored in: {db_path}")
        print("Next: run `uv run python examples/03-the-dashboard/02-dashboard-edge-cases.py`")
    finally:
        await store.close()

if __name__ == "__main__":
    asyncio.run(main(), debug=True)
