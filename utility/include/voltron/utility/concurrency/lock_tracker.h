#pragma once

#include <string>
#include <vector>

namespace voltron::utility::concurrency {

/**
 * @brief Monitor lock acquisition order
 * 
 * TODO: Implement comprehensive lock_tracker functionality
 */
class LockTracker {
public:
    static LockTracker& instance();

    /**
     * @brief Initialize lock_tracker
     */
    void initialize();

    /**
     * @brief Shutdown lock_tracker
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    LockTracker() = default;
    ~LockTracker() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::concurrency
