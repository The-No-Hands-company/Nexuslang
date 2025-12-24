#include <voltron/utility/system/process_monitor.h>
#include <iostream>

namespace voltron::utility::system {

ProcessMonitor& ProcessMonitor::instance() {
    static ProcessMonitor instance;
    return instance;
}

void ProcessMonitor::initialize() {
    enabled_ = true;
    std::cout << "[ProcessMonitor] Initialized\n";
}

void ProcessMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[ProcessMonitor] Shutdown\n";
}

bool ProcessMonitor::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::system
