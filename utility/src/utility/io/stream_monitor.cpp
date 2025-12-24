#include <voltron/utility/io/stream_monitor.h>
#include <iostream>

namespace voltron::utility::io {

StreamMonitor& StreamMonitor::instance() {
    static StreamMonitor instance;
    return instance;
}

void StreamMonitor::initialize() {
    enabled_ = true;
    std::cout << "[StreamMonitor] Initialized\n";
}

void StreamMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[StreamMonitor] Shutdown\n";
}

bool StreamMonitor::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::io
