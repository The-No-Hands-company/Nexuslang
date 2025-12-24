#pragma once

#include <string>
#include <vector>

namespace voltron::utility::cpp23 {

/**
 * @brief Debug constexpr evaluation
 * 
 * TODO: Implement comprehensive constexpr_debugger functionality
 */
class ConstexprDebugger {
public:
    static ConstexprDebugger& instance();

    /**
     * @brief Initialize constexpr_debugger
     */
    void initialize();

    /**
     * @brief Shutdown constexpr_debugger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ConstexprDebugger() = default;
    ~ConstexprDebugger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::cpp23
