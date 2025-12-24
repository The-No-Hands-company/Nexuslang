#include <voltron/utility/metrics/metrics_exporter.h>
#include <iostream>

namespace voltron::utility::metrics {

MetricsExporter& MetricsExporter::instance() {
    static MetricsExporter instance;
    return instance;
}

void MetricsExporter::initialize() {
    enabled_ = true;
    std::cout << "[MetricsExporter] Initialized\n";
}

void MetricsExporter::shutdown() {
    enabled_ = false;
    std::cout << "[MetricsExporter] Shutdown\n";
}

bool MetricsExporter::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::metrics
