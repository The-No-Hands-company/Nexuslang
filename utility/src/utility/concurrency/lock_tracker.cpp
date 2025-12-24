#include <voltron/utility/concurrency/lock_tracker.h>
#include <iostream>

namespace voltron::utility::concurrency {

LockTracker& LockTracker::instance() {
    static LockTracker instance;
    return instance;
}

void LockTracker::initialize() {
    enabled_ = true;
    std::cout << "[LockTracker] Initialized\n";
}

void LockTracker::shutdown() {
    enabled_ = false;
    std::cout << "[LockTracker] Shutdown\n";
}

bool LockTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::concurrency
