#include <voltron/utility/network/distributed_trace_context.h>
#include <iostream>

namespace voltron::utility::network {

DistributedTraceContext& DistributedTraceContext::instance() {
    static DistributedTraceContext instance;
    return instance;
}

void DistributedTraceContext::initialize() {
    enabled_ = true;
    std::cout << "[DistributedTraceContext] Initialized\n";
}

void DistributedTraceContext::shutdown() {
    enabled_ = false;
    std::cout << "[DistributedTraceContext] Shutdown\n";
}

bool DistributedTraceContext::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::network
