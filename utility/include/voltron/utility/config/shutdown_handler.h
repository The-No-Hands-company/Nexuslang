#pragma once

#include <string>
#include <vector>

namespace voltron::utility::config {

/**
 * @brief Graceful shutdown orchestration
 * 
 * TODO: Implement comprehensive shutdown_handler functionality
 */
class ShutdownHandler {
public:
    static ShutdownHandler& instance();

    /**
     * @brief Initialize shutdown_handler
     */
    void initialize();

    /**
     * @brief Shutdown shutdown_handler
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ShutdownHandler() = default;
    ~ShutdownHandler() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::config
