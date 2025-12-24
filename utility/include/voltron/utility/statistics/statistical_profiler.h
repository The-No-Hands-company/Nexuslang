#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::statistics {

/**
 * @brief Statistical code execution profiler
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Statistics
 * @version 1.0.0
 */
class StatisticalProfiler {
public:
    /**
     * @brief Get singleton instance
     */
    static StatisticalProfiler& instance();

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
    StatisticalProfiler() = default;
    ~StatisticalProfiler() = default;
    
    // Non-copyable, non-movable
    StatisticalProfiler(const StatisticalProfiler&) = delete;
    StatisticalProfiler& operator=(const StatisticalProfiler&) = delete;
    StatisticalProfiler(StatisticalProfiler&&) = delete;
    StatisticalProfiler& operator=(StatisticalProfiler&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::statistics
