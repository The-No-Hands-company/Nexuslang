#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::workflow {

/**
 * @brief Test backwards compatibility
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Workflow
 * @version 1.0.0
 */
class BackwardsCompatibilityTester {
public:
    /**
     * @brief Get singleton instance
     */
    static BackwardsCompatibilityTester& instance();

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
    BackwardsCompatibilityTester() = default;
    ~BackwardsCompatibilityTester() = default;
    
    // Non-copyable, non-movable
    BackwardsCompatibilityTester(const BackwardsCompatibilityTester&) = delete;
    BackwardsCompatibilityTester& operator=(const BackwardsCompatibilityTester&) = delete;
    BackwardsCompatibilityTester(BackwardsCompatibilityTester&&) = delete;
    BackwardsCompatibilityTester& operator=(BackwardsCompatibilityTester&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::workflow
