#pragma once

#include <string>
#include <vector>

namespace voltron::utility::config {

/**
 * @brief Debug feature flags
 * 
 * TODO: Implement comprehensive feature_flag_debugger functionality
 */
class FeatureFlagDebugger {
public:
    static FeatureFlagDebugger& instance();

    /**
     * @brief Initialize feature_flag_debugger
     */
    void initialize();

    /**
     * @brief Shutdown feature_flag_debugger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    FeatureFlagDebugger() = default;
    ~FeatureFlagDebugger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::config
