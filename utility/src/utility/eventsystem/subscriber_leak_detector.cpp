#include <voltron/utility/eventsystem/subscriber_leak_detector.h>
#include <iostream>

namespace voltron::utility::eventsystem {

SubscriberLeakDetector& SubscriberLeakDetector::instance() {
    static SubscriberLeakDetector instance;
    return instance;
}

void SubscriberLeakDetector::initialize() {
    enabled_ = true;
}

void SubscriberLeakDetector::shutdown() {
    enabled_ = false;
}

bool SubscriberLeakDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::eventsystem
