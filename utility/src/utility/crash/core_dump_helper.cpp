#include <voltron/utility/crash/core_dump_helper.h>
#include <iostream>

namespace voltron::utility::crash {

CoreDumpHelper& CoreDumpHelper::instance() {
    static CoreDumpHelper instance;
    return instance;
}

void CoreDumpHelper::initialize() {
    enabled_ = true;
    std::cout << "[CoreDumpHelper] Initialized\n";
}

void CoreDumpHelper::shutdown() {
    enabled_ = false;
    std::cout << "[CoreDumpHelper] Shutdown\n";
}

bool CoreDumpHelper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::crash
