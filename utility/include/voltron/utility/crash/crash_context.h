#pragma once

#include <string>
#include <vector>

namespace voltron::utility::crash {

/**
 * @brief Capture CPU registers and thread states
 * 
 * TODO: Implement comprehensive crash_context functionality
 */
class CrashContext {
public:
    static CrashContext& instance();

    /**
     * @brief Initialize crash_context
     */
    void initialize();

    /**
     * @brief Shutdown crash_context
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    CrashContext() = default;
    ~CrashContext() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::crash
