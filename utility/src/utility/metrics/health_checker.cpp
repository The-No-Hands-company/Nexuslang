#include <voltron/utility/metrics/health_checker.h>
#include <iostream>

namespace voltron::utility::metrics {

HealthChecker& HealthChecker::instance() {
    static HealthChecker instance;
    return instance;
}

void HealthChecker::initialize() {
    enabled_ = true;
    std::cout << "[HealthChecker] Initialized\n";
}

void HealthChecker::shutdown() {
    enabled_ = false;
    std::cout << "[HealthChecker] Shutdown\n";
}

bool HealthChecker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::metrics
