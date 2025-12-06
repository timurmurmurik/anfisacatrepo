from __future__ import annotations

from typing import List

from physics.bodies import RigidBody, SoftBody
from world.terrain import TerrainVolume


def describe_bodies(bodies: List[RigidBody | SoftBody]) -> str:
    lines = []
    for body in bodies:
        pos = body.state.position
        vel = body.state.velocity
        lines.append(
            f"{body.name}: pos=({pos.x:.2f},{pos.y:.2f},{pos.z:.2f}) vel=({vel.x:.2f},{vel.y:.2f},{vel.z:.2f})"
        )
    return "\n".join(lines)


def terrain_overview(terrain: TerrainVolume) -> str:
    filled = len(terrain.cells)
    return (
        f"Terrain size={terrain.size} cell={terrain.cell_size}m active_cells={filled} "
        f"mass={terrain.total_mass():.2f}kg"
    )
