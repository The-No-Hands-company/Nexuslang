#include <voltron/utility/timetravel/data_snapshot_manager.h>
#include <iostream>

namespace voltron::utility::timetravel {

DataSnapshotManager& DataSnapshotManager::instance() {
    static DataSnapshotManager instance;
    return instance;
}

void DataSnapshotManager::initialize() {
    enabled_ = true;
}

void DataSnapshotManager::shutdown() {
    enabled_ = false;
}

bool DataSnapshotManager::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timetravel
