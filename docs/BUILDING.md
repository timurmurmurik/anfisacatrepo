# Building Aethra Engines (planned)

> Status: the repo currently lacks a Gradle setup. The instructions below describe the intended layout once the build files are added.

## Planned toolchain
- **Loader/MC**: Fabric for Minecraft 1.20.1.
- **Java**: 17 (matching MC 1.20.x requirements).
- **Gradle**: Fabric Loom plugin to package the mod as a `.jar`.

## Expected steps (to be implemented)
1. Add `build.gradle`, `gradle.properties`, and `settings.gradle` generated via Fabric Loom.
2. Define `modid`, version, and dependencies in `fabric.mod.json` under `src/main/resources`.
3. Place sources under `src/main/java` and assets under `src/main/resources/assets/aethra_engines/`.
4. Run `./gradlew build` to produce `build/libs/aethra_engines-<version>.jar`.

Until these files exist, the project is a design-and-API stub and will not produce a runnable mod.
