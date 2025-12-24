#pragma once

#include <string>
#include <vector>

namespace voltron::utility::cpp23 {

/**
 * @brief Track coroutine lifecycle
 * 
 * TODO: Implement comprehensive coroutine_debugger functionality
 */
class CoroutineDebugger {
public:
    static CoroutineDebugger& instance();

    /**
     * @brief Initialize coroutine_debugger
     */
    void initialize();

    /**
     * @brief Shutdown coroutine_debugger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    CoroutineDebugger() = default;
    ~CoroutineDebugger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::cpp23
