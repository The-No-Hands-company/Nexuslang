#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::orchestration {

/**
 * @brief Real-time diagnostic dashboard
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Orchestration
 * @version 1.0.0
 */
class RealTimeDashboardServer {
public:
    /**
     * @brief Get singleton instance
     */
    static RealTimeDashboardServer& instance();

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
    RealTimeDashboardServer() = default;
    ~RealTimeDashboardServer() = default;
    
    // Non-copyable, non-movable
    RealTimeDashboardServer(const RealTimeDashboardServer&) = delete;
    RealTimeDashboardServer& operator=(const RealTimeDashboardServer&) = delete;
    RealTimeDashboardServer(RealTimeDashboardServer&&) = delete;
    RealTimeDashboardServer& operator=(RealTimeDashboardServer&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::orchestration
