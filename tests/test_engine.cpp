#include "materials/materials.h"
#include "physics/physics.h"
#include "simulation/simulation.h"
#include "world/world.h"

#include <cassert>
#include <iostream>

using namespace elysium;

int main() {
    // Material blending
    MaterialProperties a{1000, 1.0, 1.0, 300, 1000};
    MaterialProperties b{2000, 5.0, 3.0, 800, 2000};
    auto mixed = a.blend(b, 0.5);
    assert(mixed.density == 1500);

    // Matter field carving
    MatterField field(8, 8, 8, &a);
    field.carveSphere(4, 4, 4, 2.5);
    size_t carved = 0;
    for (size_t z = 0; z < field.depth(); ++z) {
        for (size_t y = 0; y < field.height(); ++y) {
            for (size_t x = 0; x < field.width(); ++x) {
                if (field.at(x, y, z).properties == nullptr) carved++;
            }
        }
    }
    assert(carved > 0);

    // Physics step
    PhysicsSystem physics;
    RigidBody body;
    body.mass = 10.0;
    body.position = {0, 10, 0};
    physics.addRigidBody(body);
    physics.step(0.016, field);
    assert(physics.rigidBodies()[0].position.y < 10.0);

    Simulation sim;
    sim.step(0.016);
    auto snapshot = sim.snapshot();
    assert(!snapshot.empty());

    std::cout << "All engine scaffolding tests passed.\n";
    return 0;
}
