#include <voltron/utility/crash/crash_context.h>
#include <iostream>

namespace voltron::utility::crash {

CrashContext& CrashContext::instance() {
    static CrashContext instance;
    return instance;
}

void CrashContext::initialize() {
    enabled_ = true;
    std::cout << "[CrashContext] Initialized\n";
}

void CrashContext::shutdown() {
    enabled_ = false;
    std::cout << "[CrashContext] Shutdown\n";
}

bool CrashContext::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::crash
