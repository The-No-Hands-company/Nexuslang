#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::reversing {

/**
 * @brief Detect function hooking
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Reversing
 * @version 1.0.0
 */
class HookDetector {
public:
    /**
     * @brief Get singleton instance
     */
    static HookDetector& instance();

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
    HookDetector() = default;
    ~HookDetector() = default;
    
    // Non-copyable, non-movable
    HookDetector(const HookDetector&) = delete;
    HookDetector& operator=(const HookDetector&) = delete;
    HookDetector(HookDetector&&) = delete;
    HookDetector& operator=(HookDetector&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::reversing
