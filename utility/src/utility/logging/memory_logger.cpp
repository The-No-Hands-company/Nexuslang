#include <voltron/utility/logging/memory_logger.h>
#include <iostream>

namespace voltron::utility::logging {

MemoryLogger& MemoryLogger::instance() {
    static MemoryLogger instance;
    return instance;
}

void MemoryLogger::initialize() {
    enabled_ = true;
    std::cout << "[MemoryLogger] Initialized\n";
}

void MemoryLogger::shutdown() {
    enabled_ = false;
    std::cout << "[MemoryLogger] Shutdown\n";
}

bool MemoryLogger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::logging
