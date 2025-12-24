#pragma once

#include <string>
#include <vector>

namespace voltron::utility::logging {

/**
 * @brief Automatic log file rotation
 * 
 * TODO: Implement comprehensive log_rotation functionality
 */
class LogRotation {
public:
    static LogRotation& instance();

    /**
     * @brief Initialize log_rotation
     */
    void initialize();

    /**
     * @brief Shutdown log_rotation
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    LogRotation() = default;
    ~LogRotation() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::logging
