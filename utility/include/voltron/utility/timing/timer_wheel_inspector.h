#pragma once

#include <string>
#include <vector>

namespace voltron::utility::timing {

/**
 * @brief Inspect timer wheel state
 * 
 * TODO: Implement comprehensive timer_wheel_inspector functionality
 */
class TimerWheelInspector {
public:
    static TimerWheelInspector& instance();

    /**
     * @brief Initialize timer_wheel_inspector
     */
    void initialize();

    /**
     * @brief Shutdown timer_wheel_inspector
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    TimerWheelInspector() = default;
    ~TimerWheelInspector() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::timing
