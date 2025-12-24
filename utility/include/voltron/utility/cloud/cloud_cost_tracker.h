#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::cloud {

/**
 * @brief Track cloud resource costs
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Cloud
 * @version 1.0.0
 */
class CloudCostTracker {
public:
    /**
     * @brief Get singleton instance
     */
    static CloudCostTracker& instance();

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
    CloudCostTracker() = default;
    ~CloudCostTracker() = default;
    
    // Non-copyable, non-movable
    CloudCostTracker(const CloudCostTracker&) = delete;
    CloudCostTracker& operator=(const CloudCostTracker&) = delete;
    CloudCostTracker(CloudCostTracker&&) = delete;
    CloudCostTracker& operator=(CloudCostTracker&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::cloud
