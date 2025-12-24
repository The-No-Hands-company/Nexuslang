#pragma once

#include <string>
#include <vector>

namespace voltron::utility::timing {

/**
 * @brief Mock time for testing
 * 
 * TODO: Implement comprehensive time_travel_debugger functionality
 */
class TimeTravelDebugger {
public:
    static TimeTravelDebugger& instance();

    /**
     * @brief Initialize time_travel_debugger
     */
    void initialize();

    /**
     * @brief Shutdown time_travel_debugger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    TimeTravelDebugger() = default;
    ~TimeTravelDebugger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::timing
