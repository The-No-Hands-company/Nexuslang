#pragma once

#include <string>
#include <vector>

namespace voltron::utility::network {

/**
 * @brief Debug retry logic
 * 
 * TODO: Implement comprehensive retry_policy_debugger functionality
 */
class RetryPolicyDebugger {
public:
    static RetryPolicyDebugger& instance();

    /**
     * @brief Initialize retry_policy_debugger
     */
    void initialize();

    /**
     * @brief Shutdown retry_policy_debugger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    RetryPolicyDebugger() = default;
    ~RetryPolicyDebugger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::network
