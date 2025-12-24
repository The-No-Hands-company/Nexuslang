#include <voltron/utility/logging/log_rotation.h>
#include <iostream>

namespace voltron::utility::logging {

LogRotation& LogRotation::instance() {
    static LogRotation instance;
    return instance;
}

void LogRotation::initialize() {
    enabled_ = true;
    std::cout << "[LogRotation] Initialized\n";
}

void LogRotation::shutdown() {
    enabled_ = false;
    std::cout << "[LogRotation] Shutdown\n";
}

bool LogRotation::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::logging
