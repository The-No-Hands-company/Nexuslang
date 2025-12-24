#include <voltron/utility/network/circuit_breaker_monitor.h>
#include <iostream>

namespace voltron::utility::network {

CircuitBreakerMonitor& CircuitBreakerMonitor::instance() {
    static CircuitBreakerMonitor instance;
    return instance;
}

void CircuitBreakerMonitor::initialize() {
    enabled_ = true;
    std::cout << "[CircuitBreakerMonitor] Initialized\n";
}

void CircuitBreakerMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[CircuitBreakerMonitor] Shutdown\n";
}

bool CircuitBreakerMonitor::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::network
