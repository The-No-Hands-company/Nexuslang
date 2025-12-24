#include <voltron/utility/eventsystem/event_replay_recorder.h>
#include <iostream>

namespace voltron::utility::eventsystem {

EventReplayRecorder& EventReplayRecorder::instance() {
    static EventReplayRecorder instance;
    return instance;
}

void EventReplayRecorder::initialize() {
    enabled_ = true;
}

void EventReplayRecorder::shutdown() {
    enabled_ = false;
}

bool EventReplayRecorder::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::eventsystem
