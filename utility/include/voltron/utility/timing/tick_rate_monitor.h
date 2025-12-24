#pragma once

#include <string>
#include <vector>

namespace voltron::utility::timing {

/**
 * @brief Monitor event loop timing
 * 
 * TODO: Implement comprehensive tick_rate_monitor functionality
 */
class TickRateMonitor {
public:
    static TickRateMonitor& instance();

    /**
     * @brief Initialize tick_rate_monitor
     */
    void initialize();

    /**
     * @brief Shutdown tick_rate_monitor
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    TickRateMonitor() = default;
    ~TickRateMonitor() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::timing
