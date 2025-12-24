#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::container {

/**
 * @brief Monitor container resource usage
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Container
 * @version 1.0.0
 */
class ContainerResourceMonitor {
public:
    /**
     * @brief Get singleton instance
     */
    static ContainerResourceMonitor& instance();

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
    ContainerResourceMonitor() = default;
    ~ContainerResourceMonitor() = default;
    
    // Non-copyable, non-movable
    ContainerResourceMonitor(const ContainerResourceMonitor&) = delete;
    ContainerResourceMonitor& operator=(const ContainerResourceMonitor&) = delete;
    ContainerResourceMonitor(ContainerResourceMonitor&&) = delete;
    ContainerResourceMonitor& operator=(ContainerResourceMonitor&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::container
