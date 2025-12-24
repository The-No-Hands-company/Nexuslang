#include <voltron/utility/error/errno_tracker.h>
#include <iostream>

namespace voltron::utility::error {

ErrnoTracker& ErrnoTracker::instance() {
    static ErrnoTracker instance;
    return instance;
}

void ErrnoTracker::initialize() {
    enabled_ = true;
    std::cout << "[ErrnoTracker] Initialized\n";
}

void ErrnoTracker::shutdown() {
    enabled_ = false;
    std::cout << "[ErrnoTracker] Shutdown\n";
}

bool ErrnoTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::error
