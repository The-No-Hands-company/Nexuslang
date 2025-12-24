#pragma once

#include <string>
#include <vector>

namespace voltron::utility::statemachine {

/**
 * @brief Debug distributed transactions
 * 
 * TODO: Implement comprehensive saga_debugger functionality
 */
class SagaDebugger {
public:
    static SagaDebugger& instance();

    /**
     * @brief Initialize saga_debugger
     */
    void initialize();

    /**
     * @brief Shutdown saga_debugger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    SagaDebugger() = default;
    ~SagaDebugger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::statemachine
