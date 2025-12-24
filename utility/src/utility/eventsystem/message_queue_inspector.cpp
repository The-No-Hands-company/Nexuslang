#include <voltron/utility/eventsystem/message_queue_inspector.h>
#include <iostream>

namespace voltron::utility::eventsystem {

MessageQueueInspector& MessageQueueInspector::instance() {
    static MessageQueueInspector instance;
    return instance;
}

void MessageQueueInspector::initialize() {
    enabled_ = true;
}

void MessageQueueInspector::shutdown() {
    enabled_ = false;
}

bool MessageQueueInspector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::eventsystem
