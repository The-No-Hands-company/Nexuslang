#pragma once

#include <string>
#include <vector>

namespace voltron::utility::network {

/**
 * @brief Debug gRPC calls
 * 
 * TODO: Implement comprehensive grpc_interceptor_debug functionality
 */
class GrpcInterceptorDebug {
public:
    static GrpcInterceptorDebug& instance();

    /**
     * @brief Initialize grpc_interceptor_debug
     */
    void initialize();

    /**
     * @brief Shutdown grpc_interceptor_debug
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    GrpcInterceptorDebug() = default;
    ~GrpcInterceptorDebug() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::network
