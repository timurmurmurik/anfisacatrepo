#include "simulation.h"

namespace elysium {

Simulation::Simulation()
    : materials_(defaultRegistry()),
      physics_({0, -9.81, 0}),
      field_(64, 32, 64, &materials_.propertiesFor("Water")) {}

void Simulation::step(double dt) {
    physics_.applyAerodynamics(1.225, 0.47);
    physics_.applyThermodynamics(field_, 293.15, dt);
    physics_.step(dt, field_);
}

std::string Simulation::snapshot() const {
    return field_.serialize();
}

} // namespace elysium
