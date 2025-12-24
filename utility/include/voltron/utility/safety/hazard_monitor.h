#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::safety {

/**
 * @brief Monitor hazardous system conditions
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Safety
 * @version 1.0.0
 */
class HazardMonitor {
public:
    /**
     * @brief Get singleton instance
     */
    static HazardMonitor& instance();

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
    HazardMonitor() = default;
    ~HazardMonitor() = default;
    
    // Non-copyable, non-movable
    HazardMonitor(const HazardMonitor&) = delete;
    HazardMonitor& operator=(const HazardMonitor&) = delete;
    HazardMonitor(HazardMonitor&&) = delete;
    HazardMonitor& operator=(HazardMonitor&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::safety
