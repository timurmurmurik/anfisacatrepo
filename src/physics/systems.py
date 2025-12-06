from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .bodies import AeroProfile, RigidBody, SoftBody, Vector3


@dataclass
class PhysicsConfig:
    gravity: Vector3 = field(default_factory=lambda: Vector3(0.0, -9.81, 0.0))
    ground_level: float = 0.0
    restitution: float = 0.0


class PhysicsSystem:
    def __init__(self, config: PhysicsConfig | None = None):
        self.config = config or PhysicsConfig()
        self.rigid_bodies: List[RigidBody] = []
        self.soft_bodies: List[SoftBody] = []
        self.aero_profiles: dict[str, AeroProfile] = {}

    def add_rigid_body(self, body: RigidBody, aero: AeroProfile | None = None) -> None:
        self.rigid_bodies.append(body)
        if aero:
            self.aero_profiles[body.name] = aero

    def add_soft_body(self, body: SoftBody, aero: AeroProfile | None = None) -> None:
        self.soft_bodies.append(body)
        if aero:
            self.aero_profiles[body.name] = aero

    def apply_global_forces(self, dt: float) -> None:
        for body in [*self.rigid_bodies, *self.soft_bodies]:
            body.apply_force(self.config.gravity * body.mass)
            if body.name in self.aero_profiles:
                drag = self.aero_profiles[body.name].drag_force(body.state.velocity)
                body.apply_force(drag)

    def resolve_ground_collisions(self) -> None:
        for body in [*self.rigid_bodies, *self.soft_bodies]:
            body.collide_with_ground(self.config.restitution)

    def step(self, dt: float) -> None:
        self.apply_global_forces(dt)
        for body in self.rigid_bodies:
            body.integrate(dt)
        for body in self.soft_bodies:
            body.integrate(dt)
        self.resolve_ground_collisions()
