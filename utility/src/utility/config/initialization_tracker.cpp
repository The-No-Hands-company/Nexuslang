#include <voltron/utility/config/initialization_tracker.h>
#include <iostream>

namespace voltron::utility::config {

InitializationTracker& InitializationTracker::instance() {
    static InitializationTracker instance;
    return instance;
}

void InitializationTracker::initialize() {
    enabled_ = true;
    std::cout << "[InitializationTracker] Initialized\n";
}

void InitializationTracker::shutdown() {
    enabled_ = false;
    std::cout << "[InitializationTracker] Shutdown\n";
}

bool InitializationTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::config
