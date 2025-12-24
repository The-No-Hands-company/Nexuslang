#include <voltron/utility/error/error_propagation_tracer.h>
#include <iostream>

namespace voltron::utility::error {

ErrorPropagationTracer& ErrorPropagationTracer::instance() {
    static ErrorPropagationTracer instance;
    return instance;
}

void ErrorPropagationTracer::initialize() {
    enabled_ = true;
    std::cout << "[ErrorPropagationTracer] Initialized\n";
}

void ErrorPropagationTracer::shutdown() {
    enabled_ = false;
    std::cout << "[ErrorPropagationTracer] Shutdown\n";
}

bool ErrorPropagationTracer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::error
