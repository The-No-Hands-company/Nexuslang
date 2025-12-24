#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::chaos {

/**
 * @brief Simulate service dependency failures
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Chaos
 * @version 1.0.0
 */
class DependencyFailureSimulator {
public:
    /**
     * @brief Get singleton instance
     */
    static DependencyFailureSimulator& instance();

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
    DependencyFailureSimulator() = default;
    ~DependencyFailureSimulator() = default;
    
    // Non-copyable, non-movable
    DependencyFailureSimulator(const DependencyFailureSimulator&) = delete;
    DependencyFailureSimulator& operator=(const DependencyFailureSimulator&) = delete;
    DependencyFailureSimulator(DependencyFailureSimulator&&) = delete;
    DependencyFailureSimulator& operator=(DependencyFailureSimulator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::chaos
