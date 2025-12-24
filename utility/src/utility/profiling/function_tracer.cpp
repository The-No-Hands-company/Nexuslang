#include <voltron/utility/profiling/function_tracer.h>
#include <iostream>

namespace voltron::utility::profiling {

FunctionTracer& FunctionTracer::instance() {
    static FunctionTracer instance;
    return instance;
}

void FunctionTracer::initialize() {
    enabled_ = true;
    std::cout << "[FunctionTracer] Initialized\n";
}

void FunctionTracer::shutdown() {
    enabled_ = false;
    std::cout << "[FunctionTracer] Shutdown\n";
}

bool FunctionTracer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::profiling
