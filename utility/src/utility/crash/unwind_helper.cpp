#include <voltron/utility/crash/unwind_helper.h>
#include <iostream>

namespace voltron::utility::crash {

UnwindHelper& UnwindHelper::instance() {
    static UnwindHelper instance;
    return instance;
}

void UnwindHelper::initialize() {
    enabled_ = true;
    std::cout << "[UnwindHelper] Initialized\n";
}

void UnwindHelper::shutdown() {
    enabled_ = false;
    std::cout << "[UnwindHelper] Shutdown\n";
}

bool UnwindHelper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::crash
