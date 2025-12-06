#pragma once

#include <string>
#include <unordered_map>
#include <vector>

namespace elysium {

struct MaterialProperties {
    double density;            // kg/m^3
    double hardness;           // dimensionless hardness proxy
    double thermalConductivity; // W/(m*K)
    double meltingPoint;       // Kelvin
    double specificHeat;       // J/(kg*K)
    double porosity = 0.0;     // 0..1

    MaterialProperties blend(const MaterialProperties &other, double ratio) const;
};

struct Element {
    std::string name;
    std::string symbol;
    double atomicWeight;
    MaterialProperties properties;
};

struct CompoundComponent {
    const Element *element;
    double ratio;
};

struct Compound {
    std::string name;
    std::vector<CompoundComponent> components;
    MaterialProperties properties;
};

class MaterialRegistry {
public:
    void registerElement(Element element);
    void registerCompound(Compound compound);

    const MaterialProperties &propertiesFor(const std::string &name) const;
    const Element *getElement(const std::string &name) const;
    const Compound *getCompound(const std::string &name) const;

    std::string serialize() const;
    static MaterialRegistry deserialize(const std::string &data);

private:
    std::unordered_map<std::string, Element> elements_;
    std::unordered_map<std::string, Compound> compounds_;
};

MaterialRegistry defaultRegistry();

} // namespace elysium
