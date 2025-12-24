#include <voltron/utility/metrics/metrics_collector.h>
#include <iostream>

namespace voltron::utility::metrics {

MetricsCollector& MetricsCollector::instance() {
    static MetricsCollector instance;
    return instance;
}

void MetricsCollector::initialize() {
    enabled_ = true;
    std::cout << "[MetricsCollector] Initialized\n";
}

void MetricsCollector::shutdown() {
    enabled_ = false;
    std::cout << "[MetricsCollector] Shutdown\n";
}

bool MetricsCollector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::metrics
