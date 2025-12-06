from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, Tuple
import json

from core.materials import MaterialProperties


@dataclass
class VoxelCell:
    material: str
    density: float


@dataclass
class TerrainVolume:
    """Continuous volumetric terrain made of voxel cells."""

    size: Tuple[int, int, int]
    cell_size: float
    default_material: str = "Air"
    default_density: float = 1.225
    cells: Dict[Tuple[int, int, int], VoxelCell] = field(default_factory=dict)

    def _clamp_coords(self, coords: Tuple[int, int, int]) -> Tuple[int, int, int]:
        x, y, z = coords
        max_x, max_y, max_z = self.size
        return (
            max(0, min(max_x - 1, x)),
            max(0, min(max_y - 1, y)),
            max(0, min(max_z - 1, z)),
        )

    def set_cell(self, coords: Tuple[int, int, int], material: str, density: float) -> None:
        coords = self._clamp_coords(coords)
        self.cells[coords] = VoxelCell(material=material, density=density)

    def remove_cell(self, coords: Tuple[int, int, int]) -> None:
        coords = self._clamp_coords(coords)
        self.cells.pop(coords, None)

    def carve_sphere(self, center: Tuple[int, int, int], radius: float, debris_material: str = "Air") -> None:
        cx, cy, cz = center
        for x in range(int(cx - radius), int(cx + radius) + 1):
            for y in range(int(cy - radius), int(cy + radius) + 1):
                for z in range(int(cz - radius), int(cz + radius) + 1):
                    if (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2 <= radius ** 2:
                        self.set_cell((x, y, z), debris_material, self.default_density)

    def cell_mass(self, coords: Tuple[int, int, int]) -> float:
        cell = self.cells.get(self._clamp_coords(coords))
        if not cell:
            return 0.0
        volume = self.cell_size ** 3
        return cell.density * volume

    def total_mass(self) -> float:
        return sum(self.cell_mass(coords) for coords in self.cells)

    def serialize(self) -> str:
        payload = {
            "size": self.size,
            "cell_size": self.cell_size,
            "default_material": self.default_material,
            "default_density": self.default_density,
            "cells": [
                {"coords": coords, "material": cell.material, "density": cell.density}
                for coords, cell in self.cells.items()
            ],
        }
        return json.dumps(payload, indent=2)

    @classmethod
    def deserialize(cls, raw: str) -> "TerrainVolume":
        data = json.loads(raw)
        terrain = cls(
            size=tuple(data["size"]),
            cell_size=data["cell_size"],
            default_material=data.get("default_material", "Air"),
            default_density=data.get("default_density", 1.225),
        )
        for entry in data.get("cells", []):
            terrain.set_cell(tuple(entry["coords"]), entry["material"], entry["density"])
        return terrain


@dataclass
class DestructionBehavior:
    fracture_threshold: float
    vaporize_threshold: float
    debris_material: str = "Debris"

    def apply_damage(self, terrain: TerrainVolume, coords: Tuple[int, int, int], impulse: float) -> None:
        if impulse >= self.vaporize_threshold:
            terrain.remove_cell(coords)
        elif impulse >= self.fracture_threshold:
            terrain.set_cell(coords, self.debris_material, terrain.default_density)


@dataclass
class MaterialResponse:
    properties: MaterialProperties
    destruction: DestructionBehavior

    def heat_exchange(self, temperature: float, environment_temp: float, dt: float) -> float:
        delta = environment_temp - temperature
        return temperature + delta * self.properties.thermal_conductivity * dt
