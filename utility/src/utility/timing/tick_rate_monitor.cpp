#include <voltron/utility/timing/tick_rate_monitor.h>
#include <iostream>

namespace voltron::utility::timing {

TickRateMonitor& TickRateMonitor::instance() {
    static TickRateMonitor instance;
    return instance;
}

void TickRateMonitor::initialize() {
    enabled_ = true;
    std::cout << "[TickRateMonitor] Initialized\n";
}

void TickRateMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[TickRateMonitor] Shutdown\n";
}

bool TickRateMonitor::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timing
