#include <voltron/utility/concurrency/atomic_debugger.h>
#include <iostream>

namespace voltron::utility::concurrency {

AtomicDebugger& AtomicDebugger::instance() {
    static AtomicDebugger instance;
    return instance;
}

void AtomicDebugger::initialize() {
    enabled_ = true;
    std::cout << "[AtomicDebugger] Initialized\n";
}

void AtomicDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[AtomicDebugger] Shutdown\n";
}

bool AtomicDebugger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::concurrency
