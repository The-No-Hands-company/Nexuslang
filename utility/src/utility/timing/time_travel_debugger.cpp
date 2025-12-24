#include <voltron/utility/timing/time_travel_debugger.h>
#include <iostream>

namespace voltron::utility::timing {

TimeTravelDebugger& TimeTravelDebugger::instance() {
    static TimeTravelDebugger instance;
    return instance;
}

void TimeTravelDebugger::initialize() {
    enabled_ = true;
    std::cout << "[TimeTravelDebugger] Initialized\n";
}

void TimeTravelDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[TimeTravelDebugger] Shutdown\n";
}

bool TimeTravelDebugger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timing
