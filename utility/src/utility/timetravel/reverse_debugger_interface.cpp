#include <voltron/utility/timetravel/reverse_debugger_interface.h>
#include <iostream>

namespace voltron::utility::timetravel {

ReverseDebuggerInterface& ReverseDebuggerInterface::instance() {
    static ReverseDebuggerInterface instance;
    return instance;
}

void ReverseDebuggerInterface::initialize() {
    enabled_ = true;
}

void ReverseDebuggerInterface::shutdown() {
    enabled_ = false;
}

bool ReverseDebuggerInterface::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timetravel
