#include <voltron/utility/reflection/method_tracer.h>
#include <iostream>

namespace voltron::utility::reflection {

MethodTracer& MethodTracer::instance() {
    static MethodTracer instance;
    return instance;
}

void MethodTracer::initialize() {
    enabled_ = true;
    std::cout << "[MethodTracer] Initialized\n";
}

void MethodTracer::shutdown() {
    enabled_ = false;
    std::cout << "[MethodTracer] Shutdown\n";
}

bool MethodTracer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::reflection
