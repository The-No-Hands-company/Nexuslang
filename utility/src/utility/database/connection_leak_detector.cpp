#include <voltron/utility/database/connection_leak_detector.h>
#include <iostream>

namespace voltron::utility::database {

ConnectionLeakDetector& ConnectionLeakDetector::instance() {
    static ConnectionLeakDetector instance;
    return instance;
}

void ConnectionLeakDetector::initialize() {
    enabled_ = true;
    std::cout << "[ConnectionLeakDetector] Initialized\n";
}

void ConnectionLeakDetector::shutdown() {
    enabled_ = false;
    std::cout << "[ConnectionLeakDetector] Shutdown\n";
}

bool ConnectionLeakDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::database
