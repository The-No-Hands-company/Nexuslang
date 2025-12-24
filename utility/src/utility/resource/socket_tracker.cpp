#include <voltron/utility/resource/socket_tracker.h>
#include <iostream>

namespace voltron::utility::resource {

SocketTracker& SocketTracker::instance() {
    static SocketTracker instance;
    return instance;
}

void SocketTracker::initialize() {
    enabled_ = true;
    std::cout << "[SocketTracker] Initialized\n";
}

void SocketTracker::shutdown() {
    enabled_ = false;
    std::cout << "[SocketTracker] Shutdown\n";
}

bool SocketTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::resource
