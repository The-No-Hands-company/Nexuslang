#include <voltron/utility/debug/breakpoint_helper.h>
#include <iostream>

namespace voltron::utility::debug {

BreakpointHelper& BreakpointHelper::instance() {
    static BreakpointHelper instance;
    return instance;
}

void BreakpointHelper::initialize() {
    enabled_ = true;
    std::cout << "[BreakpointHelper] Initialized\n";
}

void BreakpointHelper::shutdown() {
    enabled_ = false;
    std::cout << "[BreakpointHelper] Shutdown\n";
}

bool BreakpointHelper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::debug
