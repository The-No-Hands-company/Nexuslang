#include <voltron/utility/embedded/interrupt_latency_tracker.h>
#include <iostream>

namespace voltron::utility::embedded {

InterruptLatencyTracker& InterruptLatencyTracker::instance() {
    static InterruptLatencyTracker instance;
    return instance;
}

void InterruptLatencyTracker::initialize() {
    enabled_ = true;
}

void InterruptLatencyTracker::shutdown() {
    enabled_ = false;
}

bool InterruptLatencyTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::embedded
