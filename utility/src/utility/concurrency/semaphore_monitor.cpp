#include <voltron/utility/concurrency/semaphore_monitor.h>
#include <iostream>

namespace voltron::utility::concurrency {

SemaphoreMonitor& SemaphoreMonitor::instance() {
    static SemaphoreMonitor instance;
    return instance;
}

void SemaphoreMonitor::initialize() {
    enabled_ = true;
    std::cout << "[SemaphoreMonitor] Initialized\n";
}

void SemaphoreMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[SemaphoreMonitor] Shutdown\n";
}

bool SemaphoreMonitor::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::concurrency
