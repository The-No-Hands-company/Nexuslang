#include <voltron/utility/cpp23/coroutine_debugger.h>
#include <iostream>

namespace voltron::utility::cpp23 {

CoroutineDebugger& CoroutineDebugger::instance() {
    static CoroutineDebugger instance;
    return instance;
}

void CoroutineDebugger::initialize() {
    enabled_ = true;
    std::cout << "[CoroutineDebugger] Initialized\n";
}

void CoroutineDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[CoroutineDebugger] Shutdown\n";
}

bool CoroutineDebugger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::cpp23
