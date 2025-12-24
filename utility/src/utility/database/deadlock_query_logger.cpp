#include <voltron/utility/database/deadlock_query_logger.h>
#include <iostream>

namespace voltron::utility::database {

DeadlockQueryLogger& DeadlockQueryLogger::instance() {
    static DeadlockQueryLogger instance;
    return instance;
}

void DeadlockQueryLogger::initialize() {
    enabled_ = true;
    std::cout << "[DeadlockQueryLogger] Initialized\n";
}

void DeadlockQueryLogger::shutdown() {
    enabled_ = false;
    std::cout << "[DeadlockQueryLogger] Shutdown\n";
}

bool DeadlockQueryLogger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::database
