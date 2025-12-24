#include <voltron/utility/logging/trace_logger.h>
#include <iostream>

namespace voltron::utility::logging {

TraceLogger& TraceLogger::instance() {
    static TraceLogger instance;
    return instance;
}

void TraceLogger::initialize() {
    enabled_ = true;
    std::cout << "[TraceLogger] Initialized\n";
}

void TraceLogger::shutdown() {
    enabled_ = false;
    std::cout << "[TraceLogger] Shutdown\n";
}

bool TraceLogger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::logging
