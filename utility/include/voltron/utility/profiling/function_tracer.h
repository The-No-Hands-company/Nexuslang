#pragma once

#include <string>
#include <vector>

namespace voltron::utility::profiling {

/**
 * @brief Entry/exit tracing with call graphs
 * 
 * TODO: Implement comprehensive function_tracer functionality
 */
class FunctionTracer {
public:
    static FunctionTracer& instance();

    /**
     * @brief Initialize function_tracer
     */
    void initialize();

    /**
     * @brief Shutdown function_tracer
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    FunctionTracer() = default;
    ~FunctionTracer() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::profiling
