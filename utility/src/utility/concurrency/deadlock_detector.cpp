#include <voltron/utility/concurrency/deadlock_detector.h>
#include <iostream>

namespace voltron::utility::concurrency {

DeadlockDetector& DeadlockDetector::instance() {
    static DeadlockDetector instance;
    return instance;
}

void DeadlockDetector::initialize() {
    enabled_ = true;
    std::cout << "[DeadlockDetector] Initialized\n";
}

void DeadlockDetector::shutdown() {
    enabled_ = false;
    std::cout << "[DeadlockDetector] Shutdown\n";
}

bool DeadlockDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::concurrency
