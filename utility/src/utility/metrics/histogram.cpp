#include <voltron/utility/metrics/histogram.h>
#include <iostream>

namespace voltron::utility::metrics {

Histogram& Histogram::instance() {
    static Histogram instance;
    return instance;
}

void Histogram::initialize() {
    enabled_ = true;
    std::cout << "[Histogram] Initialized\n";
}

void Histogram::shutdown() {
    enabled_ = false;
    std::cout << "[Histogram] Shutdown\n";
}

bool Histogram::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::metrics
