#pragma once

#include <string>
#include <vector>

namespace voltron::utility::timing {

/**
 * @brief Debug task scheduling
 * 
 * TODO: Implement comprehensive scheduler_debugger functionality
 */
class SchedulerDebugger {
public:
    static SchedulerDebugger& instance();

    /**
     * @brief Initialize scheduler_debugger
     */
    void initialize();

    /**
     * @brief Shutdown scheduler_debugger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    SchedulerDebugger() = default;
    ~SchedulerDebugger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::timing
