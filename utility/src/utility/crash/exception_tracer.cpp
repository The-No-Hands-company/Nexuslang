#include <voltron/utility/crash/exception_tracer.h>
#include <iostream>

namespace voltron::utility::crash {

ExceptionTracer& ExceptionTracer::instance() {
    static ExceptionTracer instance;
    return instance;
}

void ExceptionTracer::initialize() {
    enabled_ = true;
    std::cout << "[ExceptionTracer] Initialized\n";
}

void ExceptionTracer::shutdown() {
    enabled_ = false;
    std::cout << "[ExceptionTracer] Shutdown\n";
}

bool ExceptionTracer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::crash
