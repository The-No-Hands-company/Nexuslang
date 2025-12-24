#pragma once

#include <string>
#include <vector>

namespace voltron::utility::error {

/**
 * @brief Track errno changes
 * 
 * TODO: Implement comprehensive errno_tracker functionality
 */
class ErrnoTracker {
public:
    static ErrnoTracker& instance();

    /**
     * @brief Initialize errno_tracker
     */
    void initialize();

    /**
     * @brief Shutdown errno_tracker
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ErrnoTracker() = default;
    ~ErrnoTracker() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::error
