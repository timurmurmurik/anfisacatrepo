#pragma once

#include "materials/materials.h"

#include <array>
#include <functional>
#include <string>
#include <vector>

namespace elysium {

struct MatterSample {
    const MaterialProperties *properties = nullptr;
    double temperature = 293.15; // Kelvin
    double mass = 0.0;
};

class MatterField {
public:
    MatterField(size_t width, size_t height, size_t depth, const MaterialProperties *defaultMaterial);

    size_t width() const { return width_; }
    size_t height() const { return height_; }
    size_t depth() const { return depth_; }

    const MatterSample &at(size_t x, size_t y, size_t z) const;
    MatterSample &at(size_t x, size_t y, size_t z);

    void applyTemperature(const std::function<double(size_t, size_t, size_t)> &deltaFn);
    void carveSphere(size_t cx, size_t cy, size_t cz, double radius);
    void addMaterial(size_t x, size_t y, size_t z, const MaterialProperties *props, double mass);

    std::string serialize() const;

private:
    size_t index(size_t x, size_t y, size_t z) const;

    size_t width_;
    size_t height_;
    size_t depth_;
    std::vector<MatterSample> samples_;
};

} // namespace elysium
