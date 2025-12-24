#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::scientific {

/**
 * @brief Monitor simulation stability
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Scientific
 * @version 1.0.0
 */
class SimulationStabilityMonitor {
public:
    /**
     * @brief Get singleton instance
     */
    static SimulationStabilityMonitor& instance();

    /**
     * @brief Initialize the utility
     * @param config Optional configuration parameters
     */
    void initialize(const std::string& config = "");

    /**
     * @brief Shutdown the utility and cleanup resources
     */
    void shutdown();

    /**
     * @brief Check if the utility is currently enabled
     */
    bool isEnabled() const;

    /**
     * @brief Enable the utility
     */
    void enable();

    /**
     * @brief Disable the utility
     */
    void disable();

    /**
     * @brief Get utility statistics/status
     */
    std::string getStatus() const;

    /**
     * @brief Reset utility state
     */
    void reset();

private:
    SimulationStabilityMonitor() = default;
    ~SimulationStabilityMonitor() = default;
    
    // Non-copyable, non-movable
    SimulationStabilityMonitor(const SimulationStabilityMonitor&) = delete;
    SimulationStabilityMonitor& operator=(const SimulationStabilityMonitor&) = delete;
    SimulationStabilityMonitor(SimulationStabilityMonitor&&) = delete;
    SimulationStabilityMonitor& operator=(SimulationStabilityMonitor&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::scientific
