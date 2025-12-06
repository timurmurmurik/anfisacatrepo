# Aethra Engines Feature Outline

This document summarizes the planned systems for the mod and how the Java scaffolding will evolve.

## Thermofluid capability
- **State**: pressure (bar), temperature (K), volume (mB), and fluid identity.
- **Handlers**: pipes, buffers, and machines expose a `ThermoFluidHandler` interface to allow pressure equalization and heat transfer.
- **Heat loss**: handlers adjust temperature each tick based on ambient conditions and insulation quality.

## Pipes and logistics
- **Classes**: copper (early, low pressure), steel (mid-tier), airophase (late-game, extreme pressure).
- **Balancing**: equalization favors stability but can trigger leaks if average pressure exceeds material limits.
- **Item transport**: pneumatic tubes reuse the pressure grid to launch item capsules.

## Machines
- **Generation**: boilers, gas detonation engines, thermal stacks.
- **Consumption**: turbines, press-capsulators, granulators, cryo-storage.
- **Modules**: heat exchangers, reducers, nozzles, catalysts, vibration dampers — combined through data-driven JSON presets.

## Automation
- Sensors for pressure, temperature, flow, and gas composition feed PID controllers that actuate valves.
- Analog/digital readouts allow remote monitoring on shared pressure trunks.

## World generation and mobs
- Calydon geodes, thermal fissures, and gas lenses deliver unique materials.
- Thermophages and gas jellies introduce environmental interactions and crafting reagents.

## Next steps
- Define serialization for `ThermoFluidStack` and network sync packets.
- Add registries for materials, fluids, and machine modules.
- Implement block entities for pipes and turbines with client-side visualization.
