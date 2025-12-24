#include <voltron/utility/eventsystem/event_correlation_tracker.h>
#include <iostream>

namespace voltron::utility::eventsystem {

EventCorrelationTracker& EventCorrelationTracker::instance() {
    static EventCorrelationTracker instance;
    return instance;
}

void EventCorrelationTracker::initialize() {
    enabled_ = true;
}

void EventCorrelationTracker::shutdown() {
    enabled_ = false;
}

bool EventCorrelationTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::eventsystem
