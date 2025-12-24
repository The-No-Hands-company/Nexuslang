#pragma once

#include <string>
#include <vector>

namespace voltron::utility::timing {

/**
 * @brief Track missed deadlines
 * 
 * TODO: Implement comprehensive deadline_monitor functionality
 */
class DeadlineMonitor {
public:
    static DeadlineMonitor& instance();

    /**
     * @brief Initialize deadline_monitor
     */
    void initialize();

    /**
     * @brief Shutdown deadline_monitor
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    DeadlineMonitor() = default;
    ~DeadlineMonitor() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::timing
