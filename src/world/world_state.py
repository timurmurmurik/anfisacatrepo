from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import List
import json

from core.materials import MaterialRegistry
from physics.bodies import BodyState, RigidBody, SoftBody, Vector3
from world.terrain import TerrainVolume


@dataclass
class WorldState:
    materials: MaterialRegistry
    terrain: TerrainVolume
    rigid_bodies: List[RigidBody] = field(default_factory=list)
    soft_bodies: List[SoftBody] = field(default_factory=list)

    def to_json(self) -> str:
        payload = {
            "materials": json.loads(self.materials.to_json()),
            "terrain": json.loads(self.terrain.serialize()),
            "rigid_bodies": [self._serialize_body(body) for body in self.rigid_bodies],
            "soft_bodies": [self._serialize_body(body) for body in self.soft_bodies],
        }
        return json.dumps(payload, indent=2)

    def _serialize_body(self, body: RigidBody | SoftBody) -> dict:
        return {
            "name": body.name,
            "mass": body.mass,
            "position": asdict(body.state.position),
            "velocity": asdict(body.state.velocity),
            "orientation": asdict(body.state.orientation),
            "type": body.__class__.__name__,
        }

    @classmethod
    def from_json(cls, raw: str) -> "WorldState":
        data = json.loads(raw)
        materials = MaterialRegistry.from_json(json.dumps(data["materials"]))
        terrain = TerrainVolume.deserialize(json.dumps(data["terrain"]))

        def deserialize_body(entry: dict) -> RigidBody:
            state = BodyState(
                position=Vector3(**entry["position"]),
                velocity=Vector3(**entry["velocity"]),
                orientation=Vector3(**entry.get("orientation", {"x": 0.0, "y": 0.0, "z": 0.0})),
            )
            if entry.get("type") == "SoftBody":
                return SoftBody(name=entry["name"], mass=entry["mass"], state=state)
            return RigidBody(name=entry["name"], mass=entry["mass"], state=state)

        rigid_bodies = [deserialize_body(entry) for entry in data.get("rigid_bodies", [])]
        soft_bodies = [deserialize_body(entry) for entry in data.get("soft_bodies", [])]
        return cls(materials=materials, terrain=terrain, rigid_bodies=rigid_bodies, soft_bodies=soft_bodies)
