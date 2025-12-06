package com.aethraengines;

import java.util.List;
import java.util.function.Consumer;

/**
 * Entry point and placeholder API surface for the Aethra Engines mod.
 * <p>
 * This prototype focuses on the thermofluid capability that underpins
 * pressure-driven machinery. It is intentionally minimal and non-functional,
 * serving as scaffolding for future gameplay systems.
 */
public final class AethraEnginesMod {
    public static final String MOD_ID = "aethra_engines";

    private AethraEnginesMod() {}

    /**
     * Describes the thermodynamic state of a fluid packet.
     */
    public record ThermoFluidStack(String fluidId, double amountMb, double pressureBar, double temperatureK) {
        public ThermoFluidStack withPressure(double newPressure) {
            return new ThermoFluidStack(fluidId, amountMb, newPressure, temperatureK);
        }

        public ThermoFluidStack withTemperature(double newTemperature) {
            return new ThermoFluidStack(fluidId, amountMb, pressureBar, newTemperature);
        }
    }

    /**
     * Capability for blocks/entities that can store and exchange thermofluids.
     */
    public interface ThermoFluidHandler {
        double capacityMb();

        ThermoFluidStack peek();

        ThermoFluidStack drain(double amountMb, Action action);

        double fill(ThermoFluidStack stack, Action action);

        void tickHeatLoss(Environment environment);

        void equalizeWithNeighbors(List<ThermoFluidHandler> neighbors);
    }

    /**
     * Simplified representation of ambient conditions that affect heat loss.
     */
    public record Environment(double ambientK, double insulationFactor) {}

    /**
     * Placeholder enum for fill/drain action, mirroring common modding APIs.
     */
    public enum Action {
        SIMULATE,
        EXECUTE
    }

    /**
     * Example helper to equalize pressure across connected handlers.
     */
    public static void equalizePressure(List<ThermoFluidHandler> handlers, Consumer<ThermoFluidStack> onUpdated) {
        double totalVolume = handlers.stream().mapToDouble(ThermoFluidHandler::capacityMb).sum();
        double totalContent = handlers.stream()
                .map(ThermoFluidHandler::peek)
                .mapToDouble(ThermoFluidStack::amountMb)
                .sum();
        double averagedPressure = handlers.stream()
                .map(ThermoFluidHandler::peek)
                .mapToDouble(ThermoFluidStack::pressureBar)
                .average()
                .orElse(1.0);

        double fillPerHandler = totalContent / handlers.size();
        for (ThermoFluidHandler handler : handlers) {
            ThermoFluidStack base = handler.peek();
            ThermoFluidStack adjusted = new ThermoFluidStack(base.fluidId(), fillPerHandler, averagedPressure, base.temperatureK());
            onUpdated.accept(adjusted);
        }
    }
}
