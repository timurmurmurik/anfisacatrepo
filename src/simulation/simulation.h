#pragma once

#include "materials/materials.h"
#include "physics/physics.h"
#include "world/world.h"

#include <string>

namespace elysium {

class Simulation {
public:
    Simulation();

    void step(double dt);
    std::string snapshot() const;

    MaterialRegistry &materials() { return materials_; }
    PhysicsSystem &physics() { return physics_; }
    MatterField &world() { return field_; }

private:
    MaterialRegistry materials_;
    PhysicsSystem physics_;
    MatterField field_;
};

} // namespace elysium
