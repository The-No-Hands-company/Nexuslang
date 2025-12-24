#include <voltron/utility/timetravel/checkpoint_manager.h>
#include <iostream>

namespace voltron::utility::timetravel {

CheckpointManager& CheckpointManager::instance() {
    static CheckpointManager instance;
    return instance;
}

void CheckpointManager::initialize() {
    enabled_ = true;
}

void CheckpointManager::shutdown() {
    enabled_ = false;
}

bool CheckpointManager::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timetravel
