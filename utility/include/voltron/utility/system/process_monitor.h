#pragma once

#include <string>
#include <vector>

namespace voltron::utility::system {

/**
 * @brief Monitor child processes
 * 
 * TODO: Implement comprehensive process_monitor functionality
 */
class ProcessMonitor {
public:
    static ProcessMonitor& instance();

    /**
     * @brief Initialize process_monitor
     */
    void initialize();

    /**
     * @brief Shutdown process_monitor
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ProcessMonitor() = default;
    ~ProcessMonitor() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::system
