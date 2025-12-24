#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::statistics {

/**
 * @brief Calculate percentile distributions
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Statistics
 * @version 1.0.0
 */
class PercentileCalculator {
public:
    /**
     * @brief Get singleton instance
     */
    static PercentileCalculator& instance();

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
    PercentileCalculator() = default;
    ~PercentileCalculator() = default;
    
    // Non-copyable, non-movable
    PercentileCalculator(const PercentileCalculator&) = delete;
    PercentileCalculator& operator=(const PercentileCalculator&) = delete;
    PercentileCalculator(PercentileCalculator&&) = delete;
    PercentileCalculator& operator=(PercentileCalculator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::statistics
