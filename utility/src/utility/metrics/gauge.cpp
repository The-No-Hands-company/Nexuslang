#include <voltron/utility/metrics/gauge.h>
#include <iostream>

namespace voltron::utility::metrics {

Gauge& Gauge::instance() {
    static Gauge instance;
    return instance;
}

void Gauge::initialize() {
    enabled_ = true;
    std::cout << "[Gauge] Initialized\n";
}

void Gauge::shutdown() {
    enabled_ = false;
    std::cout << "[Gauge] Shutdown\n";
}

bool Gauge::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::metrics
