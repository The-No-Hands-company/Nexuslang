#pragma once

#include <string>
#include <vector>

namespace voltron::utility::reflection {

/**
 * @brief Trace method calls via reflection
 * 
 * TODO: Implement comprehensive method_tracer functionality
 */
class MethodTracer {
public:
    static MethodTracer& instance();

    /**
     * @brief Initialize method_tracer
     */
    void initialize();

    /**
     * @brief Shutdown method_tracer
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    MethodTracer() = default;
    ~MethodTracer() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::reflection
