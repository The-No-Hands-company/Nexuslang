#include <voltron/utility/timing/scheduler_debugger.h>
#include <iostream>

namespace voltron::utility::timing {

SchedulerDebugger& SchedulerDebugger::instance() {
    static SchedulerDebugger instance;
    return instance;
}

void SchedulerDebugger::initialize() {
    enabled_ = true;
    std::cout << "[SchedulerDebugger] Initialized\n";
}

void SchedulerDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[SchedulerDebugger] Shutdown\n";
}

bool SchedulerDebugger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timing
