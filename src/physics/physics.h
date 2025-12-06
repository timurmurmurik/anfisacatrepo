#pragma once

#include "materials/materials.h"
#include "world/world.h"

#include <vector>

namespace elysium {

struct Vec3 {
    double x{0}, y{0}, z{0};
    Vec3 operator+(const Vec3 &o) const { return {x + o.x, y + o.y, z + o.z}; }
    Vec3 operator-(const Vec3 &o) const { return {x - o.x, y - o.y, z - o.z}; }
    Vec3 operator*(double s) const { return {x * s, y * s, z * s}; }
    Vec3 &operator+=(const Vec3 &o) {
        x += o.x; y += o.y; z += o.z; return *this; }
};

struct RigidBody {
    Vec3 position;
    Vec3 velocity;
    Vec3 force;
    double mass{1.0};
    const MaterialProperties *material{nullptr};
};

struct SoftNode {
    Vec3 position;
    Vec3 velocity;
    Vec3 force;
};

struct SoftBody {
    std::vector<SoftNode> nodes;
    double damping = 0.98;
    const MaterialProperties *material{nullptr};
};

class PhysicsSystem {
public:
    explicit PhysicsSystem(Vec3 gravity = {0, -9.81, 0});

    RigidBody &addRigidBody(const RigidBody &body);
    SoftBody &addSoftBody(const SoftBody &body);

    void applyAerodynamics(double airDensity, double dragCoefficient);
    void applyThermodynamics(MatterField &field, double ambientTemperature, double dt);
    void step(double dt, MatterField &field);

    const std::vector<RigidBody> &rigidBodies() const { return rigidBodies_; }
    const std::vector<SoftBody> &softBodies() const { return softBodies_; }

private:
    Vec3 gravity_;
    std::vector<RigidBody> rigidBodies_;
    std::vector<SoftBody> softBodies_;
};

} // namespace elysium
