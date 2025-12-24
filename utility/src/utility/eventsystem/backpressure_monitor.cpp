#include <voltron/utility/eventsystem/backpressure_monitor.h>
#include <iostream>

namespace voltron::utility::eventsystem {

BackpressureMonitor& BackpressureMonitor::instance() {
    static BackpressureMonitor instance;
    return instance;
}

void BackpressureMonitor::initialize() {
    enabled_ = true;
}

void BackpressureMonitor::shutdown() {
    enabled_ = false;
}

bool BackpressureMonitor::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::eventsystem
