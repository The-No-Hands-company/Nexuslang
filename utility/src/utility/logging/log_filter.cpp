#include <voltron/utility/logging/log_filter.h>
#include <iostream>

namespace voltron::utility::logging {

LogFilter& LogFilter::instance() {
    static LogFilter instance;
    return instance;
}

void LogFilter::initialize() {
    enabled_ = true;
    std::cout << "[LogFilter] Initialized\n";
}

void LogFilter::shutdown() {
    enabled_ = false;
    std::cout << "[LogFilter] Shutdown\n";
}

bool LogFilter::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::logging
