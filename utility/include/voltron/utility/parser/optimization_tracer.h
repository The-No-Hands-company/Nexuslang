#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::parser {

/**
 * @brief Trace compiler optimization passes
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Parser
 * @version 1.0.0
 */
class OptimizationTracer {
public:
    /**
     * @brief Get singleton instance
     */
    static OptimizationTracer& instance();

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
    OptimizationTracer() = default;
    ~OptimizationTracer() = default;
    
    // Non-copyable, non-movable
    OptimizationTracer(const OptimizationTracer&) = delete;
    OptimizationTracer& operator=(const OptimizationTracer&) = delete;
    OptimizationTracer(OptimizationTracer&&) = delete;
    OptimizationTracer& operator=(OptimizationTracer&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::parser
