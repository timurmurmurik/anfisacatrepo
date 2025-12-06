from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple
import json


@dataclass
class MaterialProperties:
    """Physical properties used across physics systems."""

    density: float  # kg/m^3
    hardness: float  # Mohs scale proxy (0-10)
    thermal_conductivity: float  # W/(m·K)
    melting_point: float  # Kelvin
    specific_heat: float  # J/(kg·K)
    porosity: float = 0.0

    def blend(self, other: "MaterialProperties", ratio: float) -> "MaterialProperties":
        """Blend two property sets together."""
        ratio = max(0.0, min(1.0, ratio))
        inv = 1.0 - ratio
        return MaterialProperties(
            density=self.density * inv + other.density * ratio,
            hardness=self.hardness * inv + other.hardness * ratio,
            thermal_conductivity=self.thermal_conductivity * inv
            + other.thermal_conductivity * ratio,
            melting_point=self.melting_point * inv + other.melting_point * ratio,
            specific_heat=self.specific_heat * inv + other.specific_heat * ratio,
            porosity=self.porosity * inv + other.porosity * ratio,
        )


@dataclass
class Element:
    name: str
    symbol: str
    atomic_weight: float
    properties: MaterialProperties


@dataclass
class Compound:
    name: str
    components: List[Tuple[Element, float]]
    properties: MaterialProperties

    @classmethod
    def from_components(
        cls, name: str, components: List[Tuple[Element, float]],
    ) -> "Compound":
        total_ratio = sum(ratio for _, ratio in components)
        if total_ratio <= 0:
            raise ValueError("Compound must have positive component ratios")
        normalized = [(element, ratio / total_ratio) for element, ratio in components]
        properties = normalized[0][0].properties
        for element, ratio in normalized[1:]:
            properties = properties.blend(element.properties, ratio)
        return cls(name=name, components=normalized, properties=properties)


@dataclass
class MaterialRegistry:
    elements: Dict[str, Element] = field(default_factory=dict)
    compounds: Dict[str, Compound] = field(default_factory=dict)

    def register_element(self, element: Element) -> None:
        self.elements[element.name] = element

    def register_compound(self, compound: Compound) -> None:
        self.compounds[compound.name] = compound

    def get_properties(self, name: str) -> MaterialProperties:
        if name in self.elements:
            return self.elements[name].properties
        if name in self.compounds:
            return self.compounds[name].properties
        raise KeyError(f"Unknown material '{name}'")

    def to_json(self) -> str:
        def serialize_material(mat):
            if isinstance(mat, Element):
                return {
                    "type": "element",
                    "name": mat.name,
                    "symbol": mat.symbol,
                    "atomic_weight": mat.atomic_weight,
                    "properties": asdict(mat.properties),
                }
            return {
                "type": "compound",
                "name": mat.name,
                "components": [
                    {"element": elem.name, "ratio": ratio}
                    for elem, ratio in mat.components
                ],
                "properties": asdict(mat.properties),
            }

        payload = {
            "elements": [serialize_material(el) for el in self.elements.values()],
            "compounds": [serialize_material(cp) for cp in self.compounds.values()],
        }
        return json.dumps(payload, indent=2)

    @classmethod
    def from_json(cls, raw: str) -> "MaterialRegistry":
        data = json.loads(raw)
        registry = cls()
        name_to_element: Dict[str, Element] = {}
        for el_data in data.get("elements", []):
            props = MaterialProperties(**el_data["properties"])
            element = Element(
                name=el_data["name"],
                symbol=el_data["symbol"],
                atomic_weight=el_data["atomic_weight"],
                properties=props,
            )
            registry.register_element(element)
            name_to_element[element.name] = element

        for cp_data in data.get("compounds", []):
            props = MaterialProperties(**cp_data["properties"])
            components = [
                (name_to_element[entry["element"]], entry["ratio"])
                for entry in cp_data.get("components", [])
            ]
            compound = Compound(name=cp_data["name"], components=components, properties=props)
            registry.register_compound(compound)
        return registry


# Predefined defaults for quick sandbox composition
IRON = Element(
    name="Iron",
    symbol="Fe",
    atomic_weight=55.845,
    properties=MaterialProperties(
        density=7870,
        hardness=4.0,
        thermal_conductivity=80.4,
        melting_point=1811,
        specific_heat=449,
    ),
)

WATER = Element(
    name="Water",
    symbol="H2O",
    atomic_weight=18.015,
    properties=MaterialProperties(
        density=1000,
        hardness=0.0,
        thermal_conductivity=0.58,
        melting_point=273.15,
        specific_heat=4184,
        porosity=0.9,
    ),
)
