#include <voltron/utility/timetravel/replay_synchronizer.h>
#include <iostream>

namespace voltron::utility::timetravel {

ReplaySynchronizer& ReplaySynchronizer::instance() {
    static ReplaySynchronizer instance;
    return instance;
}

void ReplaySynchronizer::initialize() {
    enabled_ = true;
}

void ReplaySynchronizer::shutdown() {
    enabled_ = false;
}

bool ReplaySynchronizer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timetravel
