#pragma once

#include <string>
#include <vector>

namespace voltron::utility::concurrency {

/**
 * @brief Log atomic operations
 * 
 * TODO: Implement comprehensive atomic_debugger functionality
 */
class AtomicDebugger {
public:
    static AtomicDebugger& instance();

    /**
     * @brief Initialize atomic_debugger
     */
    void initialize();

    /**
     * @brief Shutdown atomic_debugger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    AtomicDebugger() = default;
    ~AtomicDebugger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::concurrency
