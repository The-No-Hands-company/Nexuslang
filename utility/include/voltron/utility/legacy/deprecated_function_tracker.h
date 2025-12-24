#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::legacy {

/**
 * @brief Track usage of deprecated functions
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Legacy
 * @version 1.0.0
 */
class DeprecatedFunctionTracker {
public:
    /**
     * @brief Get singleton instance
     */
    static DeprecatedFunctionTracker& instance();

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
    DeprecatedFunctionTracker() = default;
    ~DeprecatedFunctionTracker() = default;
    
    // Non-copyable, non-movable
    DeprecatedFunctionTracker(const DeprecatedFunctionTracker&) = delete;
    DeprecatedFunctionTracker& operator=(const DeprecatedFunctionTracker&) = delete;
    DeprecatedFunctionTracker(DeprecatedFunctionTracker&&) = delete;
    DeprecatedFunctionTracker& operator=(DeprecatedFunctionTracker&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::legacy
