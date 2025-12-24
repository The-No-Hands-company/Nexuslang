#include <voltron/utility/timetravel/deterministic_replay_helper.h>
#include <iostream>

namespace voltron::utility::timetravel {

DeterministicReplayHelper& DeterministicReplayHelper::instance() {
    static DeterministicReplayHelper instance;
    return instance;
}

void DeterministicReplayHelper::initialize() {
    enabled_ = true;
}

void DeterministicReplayHelper::shutdown() {
    enabled_ = false;
}

bool DeterministicReplayHelper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timetravel
