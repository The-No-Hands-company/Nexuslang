#include <voltron/utility/timing/deadline_monitor.h>
#include <iostream>

namespace voltron::utility::timing {

DeadlineMonitor& DeadlineMonitor::instance() {
    static DeadlineMonitor instance;
    return instance;
}

void DeadlineMonitor::initialize() {
    enabled_ = true;
    std::cout << "[DeadlineMonitor] Initialized\n";
}

void DeadlineMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[DeadlineMonitor] Shutdown\n";
}

bool DeadlineMonitor::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timing
