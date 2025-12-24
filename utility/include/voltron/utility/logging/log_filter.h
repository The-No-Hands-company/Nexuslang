#pragma once

#include <string>
#include <vector>

namespace voltron::utility::logging {

/**
 * @brief Runtime log filtering
 * 
 * TODO: Implement comprehensive log_filter functionality
 */
class LogFilter {
public:
    static LogFilter& instance();

    /**
     * @brief Initialize log_filter
     */
    void initialize();

    /**
     * @brief Shutdown log_filter
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    LogFilter() = default;
    ~LogFilter() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::logging
