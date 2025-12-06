# Aethra Engines (WIP)

This repository contains the initial scaffolding and design notes for **Aethra Engines**, a Create-inspired Minecraft mod that focuses on thermodynamics, pressure, and fluid logistics.

> Target platform: **Minecraft 1.20.1 on Fabric**. The code and APIs here assume Fabric loader + Fabric API (with Architectury considered for future multi-loader support).

## Goals
- Modular machines driven by pressure and temperature instead of traditional power systems.
- Rich fluid simulation with heat exchange, viscosity, and material-dependent pipes.
- Data-driven machine modules and recipes for easy expansion.
- World-gen content: mineral geodes, thermal fissures, and pressurized gas pockets.

## Structure
- `src/main/java/com/aethraengines/` — Core mod entry points and capability stubs.
- `docs/` — Feature overviews and JSON recipe schemas (coming soon).
- `assets/` — Placeholder for models, blockstates, and language files.

> This is a non-functional prototype intended to capture architecture and APIs. Further iterations will fill in gameplay systems, rendering, and networking.

## Development plan
1. Flesh out the thermofluid capability and pipe equalization logic.
2. Implement pressure-driven power transfer and machine modules.
3. Add block entities for pipes, turbines, and generators with data-driven tuning.
4. Integrate automation (sensors, regulators, PID controllers) and visualization widgets.
5. Populate world generation and progression, then balance with recipes and hazards.

## License
MIT (placeholder).
