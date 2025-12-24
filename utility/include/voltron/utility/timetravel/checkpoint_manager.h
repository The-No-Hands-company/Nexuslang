#pragma once

#include <string>
#include <vector>

namespace voltron::utility::timetravel {

/**
 * @brief Save/restore program state
 */
class CheckpointManager {
public:
    static CheckpointManager& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    CheckpointManager() = default;
    ~CheckpointManager() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::timetravel
