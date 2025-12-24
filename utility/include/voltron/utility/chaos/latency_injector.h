#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::chaos {

/**
 * @brief Add artificial network latency
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Chaos
 * @version 1.0.0
 */
class LatencyInjector {
public:
    /**
     * @brief Get singleton instance
     */
    static LatencyInjector& instance();

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
    LatencyInjector() = default;
    ~LatencyInjector() = default;
    
    // Non-copyable, non-movable
    LatencyInjector(const LatencyInjector&) = delete;
    LatencyInjector& operator=(const LatencyInjector&) = delete;
    LatencyInjector(LatencyInjector&&) = delete;
    LatencyInjector& operator=(LatencyInjector&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::chaos
