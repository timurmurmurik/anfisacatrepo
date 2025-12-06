#include "world.h"

#include <cmath>
#include <sstream>
#include <stdexcept>

namespace elysium {

MatterField::MatterField(size_t width, size_t height, size_t depth, const MaterialProperties *defaultMaterial)
    : width_(width), height_(height), depth_(depth), samples_(width * height * depth) {
    for (auto &sample : samples_) {
        sample.properties = defaultMaterial;
        sample.mass = defaultMaterial ? defaultMaterial->density : 0.0;
    }
}

size_t MatterField::index(size_t x, size_t y, size_t z) const { return (z * height_ + y) * width_ + x; }

const MatterSample &MatterField::at(size_t x, size_t y, size_t z) const {
    if (x >= width_ || y >= height_ || z >= depth_) throw std::out_of_range("MatterField index out of range");
    return samples_[index(x, y, z)];
}

MatterSample &MatterField::at(size_t x, size_t y, size_t z) {
    if (x >= width_ || y >= height_ || z >= depth_) throw std::out_of_range("MatterField index out of range");
    return samples_[index(x, y, z)];
}

void MatterField::applyTemperature(const std::function<double(size_t, size_t, size_t)> &deltaFn) {
    for (size_t z = 0; z < depth_; ++z) {
        for (size_t y = 0; y < height_; ++y) {
            for (size_t x = 0; x < width_; ++x) {
                auto &sample = samples_[index(x, y, z)];
                sample.temperature += deltaFn(x, y, z);
            }
        }
    }
}

void MatterField::carveSphere(size_t cx, size_t cy, size_t cz, double radius) {
    double r2 = radius * radius;
    for (size_t z = 0; z < depth_; ++z) {
        for (size_t y = 0; y < height_; ++y) {
            for (size_t x = 0; x < width_; ++x) {
                double dx = static_cast<double>(x) - cx;
                double dy = static_cast<double>(y) - cy;
                double dz = static_cast<double>(z) - cz;
                double dist2 = dx * dx + dy * dy + dz * dz;
                if (dist2 <= r2) {
                    auto &sample = samples_[index(x, y, z)];
                    sample.mass = 0.0;
                    sample.temperature = 0.0;
                    sample.properties = nullptr;
                }
            }
        }
    }
}

void MatterField::addMaterial(size_t x, size_t y, size_t z, const MaterialProperties *props, double mass) {
    auto &sample = at(x, y, z);
    sample.properties = props;
    sample.mass += mass;
}

std::string MatterField::serialize() const {
    std::ostringstream oss;
    oss << "MatterField " << width_ << " " << height_ << " " << depth_ << "\n";
    for (size_t i = 0; i < samples_.size(); ++i) {
        const auto &s = samples_[i];
        oss << s.mass << "," << s.temperature << ";";
        if ((i + 1) % width_ == 0) oss << "\n";
    }
    return oss.str();
}

} // namespace elysium
