#include <voltron/utility/eventsystem/event_ordering_validator.h>
#include <iostream>

namespace voltron::utility::eventsystem {

EventOrderingValidator& EventOrderingValidator::instance() {
    static EventOrderingValidator instance;
    return instance;
}

void EventOrderingValidator::initialize() {
    enabled_ = true;
}

void EventOrderingValidator::shutdown() {
    enabled_ = false;
}

bool EventOrderingValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::eventsystem
