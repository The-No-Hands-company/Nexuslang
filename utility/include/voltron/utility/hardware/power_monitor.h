#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::hardware {

/**
 * @brief Monitor system power consumption
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Hardware
 * @version 1.0.0
 */
class PowerMonitor {
public:
    /**
     * @brief Get singleton instance
     */
    static PowerMonitor& instance();

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
    PowerMonitor() = default;
    ~PowerMonitor() = default;
    
    // Non-copyable, non-movable
    PowerMonitor(const PowerMonitor&) = delete;
    PowerMonitor& operator=(const PowerMonitor&) = delete;
    PowerMonitor(PowerMonitor&&) = delete;
    PowerMonitor& operator=(PowerMonitor&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::hardware
