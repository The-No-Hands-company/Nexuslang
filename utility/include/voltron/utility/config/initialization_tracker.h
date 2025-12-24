#pragma once

#include <string>
#include <vector>

namespace voltron::utility::config {

/**
 * @brief Track initialization order
 * 
 * TODO: Implement comprehensive initialization_tracker functionality
 */
class InitializationTracker {
public:
    static InitializationTracker& instance();

    /**
     * @brief Initialize initialization_tracker
     */
    void initialize();

    /**
     * @brief Shutdown initialization_tracker
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    InitializationTracker() = default;
    ~InitializationTracker() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::config
