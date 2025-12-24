#include <voltron/utility/timetravel/call_history_buffer.h>
#include <iostream>

namespace voltron::utility::timetravel {

CallHistoryBuffer& CallHistoryBuffer::instance() {
    static CallHistoryBuffer instance;
    return instance;
}

void CallHistoryBuffer::initialize() {
    enabled_ = true;
}

void CallHistoryBuffer::shutdown() {
    enabled_ = false;
}

bool CallHistoryBuffer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timetravel
