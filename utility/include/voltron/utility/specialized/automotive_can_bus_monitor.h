#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::specialized {

/**
 * @brief Monitor automotive CAN bus
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Specialized
 * @version 1.0.0
 */
class AutomotiveCanBusMonitor {
public:
    /**
     * @brief Get singleton instance
     */
    static AutomotiveCanBusMonitor& instance();

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
    AutomotiveCanBusMonitor() = default;
    ~AutomotiveCanBusMonitor() = default;
    
    // Non-copyable, non-movable
    AutomotiveCanBusMonitor(const AutomotiveCanBusMonitor&) = delete;
    AutomotiveCanBusMonitor& operator=(const AutomotiveCanBusMonitor&) = delete;
    AutomotiveCanBusMonitor(AutomotiveCanBusMonitor&&) = delete;
    AutomotiveCanBusMonitor& operator=(AutomotiveCanBusMonitor&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::specialized
