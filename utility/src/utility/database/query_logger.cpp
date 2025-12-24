#include <voltron/utility/database/query_logger.h>
#include <iostream>

namespace voltron::utility::database {

QueryLogger& QueryLogger::instance() {
    static QueryLogger instance;
    return instance;
}

void QueryLogger::initialize() {
    enabled_ = true;
    std::cout << "[QueryLogger] Initialized\n";
}

void QueryLogger::shutdown() {
    enabled_ = false;
    std::cout << "[QueryLogger] Shutdown\n";
}

bool QueryLogger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::database
