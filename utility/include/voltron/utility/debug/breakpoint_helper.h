#pragma once

#include <string>
#include <vector>

namespace voltron::utility::debug {

/**
 * @brief Conditional breakpoints in code
 * 
 * TODO: Implement comprehensive breakpoint_helper functionality
 */
class BreakpointHelper {
public:
    static BreakpointHelper& instance();

    /**
     * @brief Initialize breakpoint_helper
     */
    void initialize();

    /**
     * @brief Shutdown breakpoint_helper
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    BreakpointHelper() = default;
    ~BreakpointHelper() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::debug
