#pragma once

#include <string>
#include <vector>

namespace voltron::utility::timetravel {

/**
 * @brief Snapshot data structures
 */
class DataSnapshotManager {
public:
    static DataSnapshotManager& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    DataSnapshotManager() = default;
    ~DataSnapshotManager() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::timetravel
