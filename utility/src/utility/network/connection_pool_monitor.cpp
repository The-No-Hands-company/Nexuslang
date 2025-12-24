#include <voltron/utility/network/connection_pool_monitor.h>
#include <iostream>

namespace voltron::utility::network {

ConnectionPoolMonitor& ConnectionPoolMonitor::instance() {
    static ConnectionPoolMonitor instance;
    return instance;
}

void ConnectionPoolMonitor::initialize() {
    enabled_ = true;
    std::cout << "[ConnectionPoolMonitor] Initialized\n";
}

void ConnectionPoolMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[ConnectionPoolMonitor] Shutdown\n";
}

bool ConnectionPoolMonitor::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::network
