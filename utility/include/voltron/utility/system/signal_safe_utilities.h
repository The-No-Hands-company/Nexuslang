#pragma once

#include <string>
#include <vector>

namespace voltron::utility::system {

/**
 * @brief Signal-safe logging
 * 
 * TODO: Implement comprehensive signal_safe_utilities functionality
 */
class SignalSafeUtilities {
public:
    static SignalSafeUtilities& instance();

    /**
     * @brief Initialize signal_safe_utilities
     */
    void initialize();

    /**
     * @brief Shutdown signal_safe_utilities
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    SignalSafeUtilities() = default;
    ~SignalSafeUtilities() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::system
