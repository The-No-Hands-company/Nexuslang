#include <voltron/utility/network/grpc_interceptor_debug.h>
#include <iostream>

namespace voltron::utility::network {

GrpcInterceptorDebug& GrpcInterceptorDebug::instance() {
    static GrpcInterceptorDebug instance;
    return instance;
}

void GrpcInterceptorDebug::initialize() {
    enabled_ = true;
    std::cout << "[GrpcInterceptorDebug] Initialized\n";
}

void GrpcInterceptorDebug::shutdown() {
    enabled_ = false;
    std::cout << "[GrpcInterceptorDebug] Shutdown\n";
}

bool GrpcInterceptorDebug::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::network
