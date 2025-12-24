#pragma once

#include <string>
#include <vector>

namespace voltron::utility::network {

/**
 * @brief OpenTelemetry tracing
 * 
 * TODO: Implement comprehensive distributed_trace_context functionality
 */
class DistributedTraceContext {
public:
    static DistributedTraceContext& instance();

    /**
     * @brief Initialize distributed_trace_context
     */
    void initialize();

    /**
     * @brief Shutdown distributed_trace_context
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    DistributedTraceContext() = default;
    ~DistributedTraceContext() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::network
