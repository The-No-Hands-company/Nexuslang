#include <voltron/utility/statemachine/event_sourcing_logger.h>
#include <iostream>

namespace voltron::utility::statemachine {

EventSourcingLogger& EventSourcingLogger::instance() {
    static EventSourcingLogger instance;
    return instance;
}

void EventSourcingLogger::initialize() {
    enabled_ = true;
    std::cout << "[EventSourcingLogger] Initialized\n";
}

void EventSourcingLogger::shutdown() {
    enabled_ = false;
    std::cout << "[EventSourcingLogger] Shutdown\n";
}

bool EventSourcingLogger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::statemachine
