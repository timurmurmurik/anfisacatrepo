from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List

from physics.systems import PhysicsSystem
from world.world_state import WorldState


@dataclass
class SimulationEvent:
    description: str
    time: float


@dataclass
class Simulation:
    world: WorldState
    physics: PhysicsSystem
    time: float = 0.0
    listeners: List[Callable[[SimulationEvent], None]] = field(default_factory=list)

    def step(self, dt: float) -> None:
        self.physics.step(dt)
        self.time += dt
        self._notify(SimulationEvent(description="physics_step", time=self.time))

    def run(self, duration: float, dt: float) -> None:
        steps = int(duration / dt)
        for _ in range(steps):
            self.step(dt)

    def _notify(self, event: SimulationEvent) -> None:
        for listener in self.listeners:
            listener(event)

    def add_listener(self, listener: Callable[[SimulationEvent], None]) -> None:
        self.listeners.append(listener)

    def save_state(self) -> str:
        return self.world.to_json()

    @classmethod
    def load_state(cls, raw: str, physics: PhysicsSystem) -> "Simulation":
        world = WorldState.from_json(raw)
        return cls(world=world, physics=physics)
