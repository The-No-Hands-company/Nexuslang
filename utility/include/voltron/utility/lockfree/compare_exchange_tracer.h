#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::lockfree {

/**
 * @brief Trace compare-and-swap operations
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Lockfree
 * @version 1.0.0
 */
class CompareExchangeTracer {
public:
    /**
     * @brief Get singleton instance
     */
    static CompareExchangeTracer& instance();

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
    CompareExchangeTracer() = default;
    ~CompareExchangeTracer() = default;
    
    // Non-copyable, non-movable
    CompareExchangeTracer(const CompareExchangeTracer&) = delete;
    CompareExchangeTracer& operator=(const CompareExchangeTracer&) = delete;
    CompareExchangeTracer(CompareExchangeTracer&&) = delete;
    CompareExchangeTracer& operator=(CompareExchangeTracer&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::lockfree
