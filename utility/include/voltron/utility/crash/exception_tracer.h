#pragma once

#include <string>
#include <vector>

namespace voltron::utility::crash {

/**
 * @brief Track exception throw points and propagation
 * 
 * TODO: Implement comprehensive exception_tracer functionality
 */
class ExceptionTracer {
public:
    static ExceptionTracer& instance();

    /**
     * @brief Initialize exception_tracer
     */
    void initialize();

    /**
     * @brief Shutdown exception_tracer
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ExceptionTracer() = default;
    ~ExceptionTracer() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::crash
