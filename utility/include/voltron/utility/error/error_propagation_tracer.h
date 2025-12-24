#pragma once

#include <string>
#include <vector>

namespace voltron::utility::error {

/**
 * @brief Track error code propagation
 * 
 * TODO: Implement comprehensive error_propagation_tracer functionality
 */
class ErrorPropagationTracer {
public:
    static ErrorPropagationTracer& instance();

    /**
     * @brief Initialize error_propagation_tracer
     */
    void initialize();

    /**
     * @brief Shutdown error_propagation_tracer
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ErrorPropagationTracer() = default;
    ~ErrorPropagationTracer() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::error
