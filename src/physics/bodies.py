from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional
import math


@dataclass
class Vector3:
    x: float
    y: float
    z: float

    def __add__(self, other: "Vector3") -> "Vector3":
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vector3") -> "Vector3":
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vector3":
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    __rmul__ = __mul__

    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalized(self) -> "Vector3":
        mag = self.magnitude()
        if mag == 0:
            return Vector3(0.0, 0.0, 0.0)
        return self * (1.0 / mag)


@dataclass
class BodyState:
    position: Vector3
    velocity: Vector3
    orientation: Vector3 = field(default_factory=lambda: Vector3(0.0, 0.0, 0.0))


@dataclass
class RigidBody:
    name: str
    mass: float
    state: BodyState
    forces: Vector3 = field(default_factory=lambda: Vector3(0.0, 0.0, 0.0))
    on_collision: Optional[Callable[["RigidBody"], None]] = None

    def apply_force(self, force: Vector3) -> None:
        self.forces = self.forces + force

    def integrate(self, dt: float) -> None:
        if self.mass <= 0:
            raise ValueError("Rigid body mass must be positive")
        acceleration = Vector3(
            self.forces.x / self.mass,
            self.forces.y / self.mass,
            self.forces.z / self.mass,
        )
        self.state.velocity = self.state.velocity + acceleration * dt
        self.state.position = self.state.position + self.state.velocity * dt
        self.forces = Vector3(0.0, 0.0, 0.0)

    def collide_with_ground(self, restitution: float = 0.5) -> None:
        if self.state.position.y < 0:
            self.state.position = Vector3(self.state.position.x, 0.0, self.state.position.z)
            self.state.velocity = Vector3(self.state.velocity.x, -self.state.velocity.y * restitution, self.state.velocity.z)
            if self.on_collision:
                self.on_collision(self)


@dataclass
class SoftBody(RigidBody):
    elasticity: float = 0.5
    damping: float = 0.1

    def integrate(self, dt: float) -> None:
        # Apply damping to velocity to model internal friction
        damped_velocity = self.state.velocity * (1.0 - self.damping * dt)
        self.state.velocity = damped_velocity
        super().integrate(dt)

    def deform(self, magnitude: float) -> float:
        """Returns deformation amount influenced by elasticity."""
        return magnitude * (1.0 - self.elasticity)


@dataclass
class AeroProfile:
    area: float
    drag_coefficient: float
    air_density: float = 1.225

    def drag_force(self, velocity: Vector3) -> Vector3:
        speed = velocity.magnitude()
        if speed == 0:
            return Vector3(0.0, 0.0, 0.0)
        direction = velocity.normalized()
        magnitude = 0.5 * self.air_density * (speed ** 2) * self.drag_coefficient * self.area
        return direction * -magnitude
