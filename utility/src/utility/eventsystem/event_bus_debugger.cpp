#include <voltron/utility/eventsystem/event_bus_debugger.h>
#include <iostream>

namespace voltron::utility::eventsystem {

EventBusDebugger& EventBusDebugger::instance() {
    static EventBusDebugger instance;
    return instance;
}

void EventBusDebugger::initialize() {
    enabled_ = true;
}

void EventBusDebugger::shutdown() {
    enabled_ = false;
}

bool EventBusDebugger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::eventsystem
