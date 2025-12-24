#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::license {

/**
 * @brief Track all third-party dependencies
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category License
 * @version 1.0.0
 */
class ThirdPartyTracker {
public:
    /**
     * @brief Get singleton instance
     */
    static ThirdPartyTracker& instance();

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
    ThirdPartyTracker() = default;
    ~ThirdPartyTracker() = default;
    
    // Non-copyable, non-movable
    ThirdPartyTracker(const ThirdPartyTracker&) = delete;
    ThirdPartyTracker& operator=(const ThirdPartyTracker&) = delete;
    ThirdPartyTracker(ThirdPartyTracker&&) = delete;
    ThirdPartyTracker& operator=(ThirdPartyTracker&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::license
