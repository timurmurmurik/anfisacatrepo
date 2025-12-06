import json

from core.materials import MaterialProperties, Element, MaterialRegistry
from physics.bodies import AeroProfile, BodyState, RigidBody, SoftBody, Vector3
from physics.systems import PhysicsSystem
from core.simulation import Simulation
from world.terrain import DestructionBehavior, MaterialResponse, TerrainVolume
from world.world_state import WorldState


def build_world():
    registry = MaterialRegistry()
    steel = Element(
        name="Steel",
        symbol="St",
        atomic_weight=55.0,
        properties=MaterialProperties(
            density=8050,
            hardness=5.5,
            thermal_conductivity=16.0,
            melting_point=1800,
            specific_heat=490,
        ),
    )
    registry.register_element(steel)
    terrain = TerrainVolume(size=(8, 8, 8), cell_size=1.0, default_material="Air")
    terrain.set_cell((3, 0, 3), material="Steel", density=steel.properties.density)
    return registry, terrain


def test_material_registry_roundtrip():
    registry, _ = build_world()
    raw = registry.to_json()
    loaded = MaterialRegistry.from_json(raw)
    assert loaded.get_properties("Steel").density == registry.get_properties("Steel").density


def test_rigid_body_moves_with_gravity():
    registry, terrain = build_world()
    physics = PhysicsSystem()
    state = BodyState(position=Vector3(0.0, 10.0, 0.0), velocity=Vector3(0.0, 0.0, 0.0))
    body = RigidBody(name="crate", mass=10.0, state=state)
    physics.add_rigid_body(body, aero=AeroProfile(area=1.0, drag_coefficient=0.1))
    world = WorldState(materials=registry, terrain=terrain, rigid_bodies=[body])
    sim = Simulation(world=world, physics=physics)

    sim.step(0.1)
    assert body.state.position.y < 10.0
    assert body.state.velocity.y < 0.0


def test_soft_body_deformation_and_ground_collision():
    registry, terrain = build_world()
    physics = PhysicsSystem()
    state = BodyState(position=Vector3(0.0, 1.0, 0.0), velocity=Vector3(0.0, -5.0, 0.0))
    blob = SoftBody(name="blob", mass=2.0, state=state, elasticity=0.2, damping=0.05)
    physics.add_soft_body(blob)
    world = WorldState(materials=registry, terrain=terrain, soft_bodies=[blob])
    sim = Simulation(world=world, physics=physics)

    sim.step(0.2)
    assert blob.state.position.y >= 0.0
    assert blob.state.velocity.y <= 0.0
    assert blob.deform(1.0) > 0.0


def test_world_serialization_with_terrain_and_bodies():
    registry, terrain = build_world()
    physics = PhysicsSystem()
    body_state = BodyState(position=Vector3(1.0, 2.0, 3.0), velocity=Vector3(0.1, 0.2, 0.3))
    body = RigidBody(name="probe", mass=1.0, state=body_state)
    terrain.carve_sphere((3, 0, 3), radius=1.0)
    world = WorldState(materials=registry, terrain=terrain, rigid_bodies=[body])
    serialized = world.to_json()
    restored = WorldState.from_json(serialized)

    assert restored.rigid_bodies[0].state.position.y == body_state.position.y
    assert len(restored.terrain.cells) == len(terrain.cells)


def test_destruction_behavior_modifies_cells():
    registry, terrain = build_world()
    behavior = DestructionBehavior(fracture_threshold=10.0, vaporize_threshold=50.0)
    behavior.apply_damage(terrain, (3, 0, 3), impulse=20.0)
    assert terrain.cells[(3, 0, 3)].material == behavior.debris_material
    behavior.apply_damage(terrain, (3, 0, 3), impulse=100.0)
    assert (3, 0, 3) not in terrain.cells


def test_material_response_heat_exchange_moves_temperature():
    registry, _ = build_world()
    properties = registry.get_properties("Steel")
    response = MaterialResponse(properties=properties, destruction=DestructionBehavior(5, 15))
    updated_temp = response.heat_exchange(temperature=300.0, environment_temp=400.0, dt=0.01)
    assert updated_temp > 300.0
