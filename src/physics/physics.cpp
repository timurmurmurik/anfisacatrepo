#include "physics.h"

#include <algorithm>
#include <cmath>

namespace elysium {

PhysicsSystem::PhysicsSystem(Vec3 gravity) : gravity_(gravity) {}

RigidBody &PhysicsSystem::addRigidBody(const RigidBody &body) {
    rigidBodies_.push_back(body);
    return rigidBodies_.back();
}

SoftBody &PhysicsSystem::addSoftBody(const SoftBody &body) {
    softBodies_.push_back(body);
    return softBodies_.back();
}

void PhysicsSystem::applyAerodynamics(double airDensity, double dragCoefficient) {
    for (auto &body : rigidBodies_) {
        double speed = std::sqrt(body.velocity.x * body.velocity.x + body.velocity.y * body.velocity.y + body.velocity.z * body.velocity.z);
        double dragMagnitude = 0.5 * airDensity * speed * speed * dragCoefficient;
        Vec3 drag = body.velocity * (-dragMagnitude / (speed + 1e-6));
        body.force += drag;
    }
}

void PhysicsSystem::applyThermodynamics(MatterField &field, double ambientTemperature, double dt) {
    field.applyTemperature([&](size_t, size_t, size_t) {
        return (ambientTemperature - 293.15) * dt * 0.1;
    });
}

void PhysicsSystem::step(double dt, MatterField &field) {
    for (auto &body : rigidBodies_) {
        body.force += gravity_ * body.mass;
        Vec3 acceleration = body.force * (1.0 / body.mass);
        body.velocity += acceleration * dt;
        body.position += body.velocity * dt;
        body.force = {0, 0, 0};

        // crude ground collision against y=0 plane
        if (body.position.y < 0) {
            body.position.y = 0;
            body.velocity.y *= -0.4; // restitution
        }
    }

    for (auto &soft : softBodies_) {
        for (auto &node : soft.nodes) {
            node.force += gravity_;
            node.velocity += node.force * dt;
            node.position += node.velocity * dt;
            node.force = {0, 0, 0};
            node.velocity = node.velocity * soft.damping;
        }
    }

    // simple coupling: deposit heat from field into soft bodies if embedded
    for (auto &soft : softBodies_) {
        for (auto &node : soft.nodes) {
            size_t x = static_cast<size_t>(std::clamp(node.position.x, 0.0, static_cast<double>(field.width() - 1)));
            size_t y = static_cast<size_t>(std::clamp(node.position.y, 0.0, static_cast<double>(field.height() - 1)));
            size_t z = static_cast<size_t>(std::clamp(node.position.z, 0.0, static_cast<double>(field.depth() - 1)));
            auto &sample = field.at(x, y, z);
            if (sample.properties) {
                double energy = sample.mass * sample.properties->specificHeat * (sample.temperature - 293.15);
                sample.temperature = std::max(0.0, sample.temperature - dt * 0.5);
                node.velocity.y += energy * 1e-6; // buoyancy-like lift
            }
        }
    }
}

} // namespace elysium
