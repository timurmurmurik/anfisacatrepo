#include "materials.h"

#include <algorithm>
#include <cmath>
#include <sstream>
#include <stdexcept>

namespace elysium {

MaterialProperties MaterialProperties::blend(const MaterialProperties &other, double ratio) const {
    ratio = std::clamp(ratio, 0.0, 1.0);
    const double inv = 1.0 - ratio;
    return {
        density * inv + other.density * ratio,
        hardness * inv + other.hardness * ratio,
        thermalConductivity * inv + other.thermalConductivity * ratio,
        meltingPoint * inv + other.meltingPoint * ratio,
        specificHeat * inv + other.specificHeat * ratio,
        porosity * inv + other.porosity * ratio,
    };
}

void MaterialRegistry::registerElement(Element element) { elements_.insert_or_assign(element.name, std::move(element)); }

void MaterialRegistry::registerCompound(Compound compound) { compounds_.insert_or_assign(compound.name, std::move(compound)); }

const MaterialProperties &MaterialRegistry::propertiesFor(const std::string &name) const {
    if (auto it = elements_.find(name); it != elements_.end()) {
        return it->second.properties;
    }
    if (auto it = compounds_.find(name); it != compounds_.end()) {
        return it->second.properties;
    }
    throw std::out_of_range("Unknown material: " + name);
}

const Element *MaterialRegistry::getElement(const std::string &name) const {
    if (auto it = elements_.find(name); it != elements_.end()) {
        return &it->second;
    }
    return nullptr;
}

const Compound *MaterialRegistry::getCompound(const std::string &name) const {
    if (auto it = compounds_.find(name); it != compounds_.end()) {
        return &it->second;
    }
    return nullptr;
}

std::string MaterialRegistry::serialize() const {
    std::ostringstream oss;
    oss << "{\n  \"elements\": [\n";
    bool first = true;
    for (const auto &entry : elements_) {
        if (!first) oss << ",\n";
        first = false;
        const auto &el = entry.second;
        oss << "    {\"name\": \"" << el.name << "\", \"symbol\": \"" << el.symbol << "\", "
            "\"atomicWeight\": " << el.atomicWeight << ", \"properties\": {"
            "\"density\": " << el.properties.density << ", \"hardness\": " << el.properties.hardness
            << ", \"thermalConductivity\": " << el.properties.thermalConductivity
            << ", \"meltingPoint\": " << el.properties.meltingPoint << ", \"specificHeat\": "
            << el.properties.specificHeat << ", \"porosity\": " << el.properties.porosity << "}}";
    }
    oss << "\n  ],\n  \"compounds\": [\n";
    first = true;
    for (const auto &entry : compounds_) {
        if (!first) oss << ",\n";
        first = false;
        const auto &cp = entry.second;
        oss << "    {\"name\": \"" << cp.name << "\", \"properties\": {"
            "\"density\": " << cp.properties.density << ", \"hardness\": " << cp.properties.hardness
            << ", \"thermalConductivity\": " << cp.properties.thermalConductivity
            << ", \"meltingPoint\": " << cp.properties.meltingPoint << ", \"specificHeat\": "
            << cp.properties.specificHeat << ", \"porosity\": " << cp.properties.porosity << "}, "
            "\"components\": [";
        bool firstComp = true;
        for (const auto &comp : cp.components) {
            if (!firstComp) oss << ", ";
            firstComp = false;
            oss << "{\"element\": \"" << comp.element->name << "\", \"ratio\": " << comp.ratio << "}";
        }
        oss << "]}";
    }
    oss << "\n  ]\n}\n";
    return oss.str();
}

MaterialRegistry MaterialRegistry::deserialize(const std::string &data) {
    // Lightweight deserializer that expects the serialize() format; not general JSON parsing.
    MaterialRegistry registry;
    // Very simple line-based parser
    std::istringstream iss(data);
    std::string line;
    enum class Section { None, Elements, Compounds } section = Section::None;
    while (std::getline(iss, line)) {
        if (line.find("\"elements\"") != std::string::npos) {
            section = Section::Elements;
            continue;
        }
        if (line.find("\"compounds\"") != std::string::npos) {
            section = Section::Compounds;
            continue;
        }
        if (line.find("{") == std::string::npos || line.find("}") == std::string::npos) {
            continue;
        }
        if (section == Section::Elements) {
            Element el{};
            // naive parsing; assumes serialize formatting
            auto namePos = line.find("\"name\": \"");
            auto symPos = line.find("\"symbol\": \"");
            auto awPos = line.find("\"atomicWeight\": ");
            auto propPos = line.find("\"properties\": {");
            if (namePos == std::string::npos || symPos == std::string::npos || awPos == std::string::npos || propPos == std::string::npos)
                continue;
            namePos += 9;
            auto nameEnd = line.find("\"", namePos);
            el.name = line.substr(namePos, nameEnd - namePos);
            symPos += 11;
            auto symEnd = line.find("\"", symPos);
            el.symbol = line.substr(symPos, symEnd - symPos);
            awPos += 17;
            el.atomicWeight = std::stod(line.substr(awPos));
            // simple properties extraction
            auto densPos = line.find("\"density\": ");
            auto hardPos = line.find("\"hardness\": ");
            auto tcPos = line.find("\"thermalConductivity\": ");
            auto mpPos = line.find("\"meltingPoint\": ");
            auto shPos = line.find("\"specificHeat\": ");
            auto porPos = line.find("\"porosity\": ");
            if (densPos != std::string::npos && hardPos != std::string::npos && tcPos != std::string::npos &&
                mpPos != std::string::npos && shPos != std::string::npos && porPos != std::string::npos) {
                el.properties.density = std::stod(line.substr(densPos + 12));
                el.properties.hardness = std::stod(line.substr(hardPos + 12));
                el.properties.thermalConductivity = std::stod(line.substr(tcPos + 23));
                el.properties.meltingPoint = std::stod(line.substr(mpPos + 16));
                el.properties.specificHeat = std::stod(line.substr(shPos + 16));
                el.properties.porosity = std::stod(line.substr(porPos + 12));
            }
            registry.registerElement(el);
        } else if (section == Section::Compounds) {
            // For brevity, this demo parser skips compound reconstruction.
        }
    }
    return registry;
}

MaterialRegistry defaultRegistry() {
    MaterialRegistry registry;
    Element iron{"Iron", "Fe", 55.845, {7870, 4.0, 80.4, 1811, 449}};
    Element water{"Water", "H2O", 18.015, {1000, 0.0, 0.58, 273.15, 4184, 0.9}};
    registry.registerElement(iron);
    registry.registerElement(water);

    Compound steel;
    steel.name = "Steel";
    steel.components = {{registry.getElement("Iron"), 0.98}};
    steel.properties = iron.properties.blend(iron.properties, 1.0);
    registry.registerCompound(steel);

    return registry;
}

} // namespace elysium
