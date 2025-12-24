#include <voltron/utility/resource/database_connection_tracker.h>
#include <iostream>

namespace voltron::utility::resource {

DatabaseConnectionTracker& DatabaseConnectionTracker::instance() {
    static DatabaseConnectionTracker instance;
    return instance;
}

void DatabaseConnectionTracker::initialize() {
    enabled_ = true;
    std::cout << "[DatabaseConnectionTracker] Initialized\n";
}

void DatabaseConnectionTracker::shutdown() {
    enabled_ = false;
    std::cout << "[DatabaseConnectionTracker] Shutdown\n";
}

bool DatabaseConnectionTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::resource
