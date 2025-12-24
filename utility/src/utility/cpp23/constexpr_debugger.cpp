#include <voltron/utility/cpp23/constexpr_debugger.h>
#include <iostream>

namespace voltron::utility::cpp23 {

ConstexprDebugger& ConstexprDebugger::instance() {
    static ConstexprDebugger instance;
    return instance;
}

void ConstexprDebugger::initialize() {
    enabled_ = true;
    std::cout << "[ConstexprDebugger] Initialized\n";
}

void ConstexprDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[ConstexprDebugger] Shutdown\n";
}

bool ConstexprDebugger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::cpp23
