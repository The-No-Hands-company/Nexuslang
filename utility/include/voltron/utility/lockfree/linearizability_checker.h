#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::lockfree {

/**
 * @brief Check lock-free linearizability
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Lockfree
 * @version 1.0.0
 */
class LinearizabilityChecker {
public:
    /**
     * @brief Get singleton instance
     */
    static LinearizabilityChecker& instance();

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
    LinearizabilityChecker() = default;
    ~LinearizabilityChecker() = default;
    
    // Non-copyable, non-movable
    LinearizabilityChecker(const LinearizabilityChecker&) = delete;
    LinearizabilityChecker& operator=(const LinearizabilityChecker&) = delete;
    LinearizabilityChecker(LinearizabilityChecker&&) = delete;
    LinearizabilityChecker& operator=(LinearizabilityChecker&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::lockfree
