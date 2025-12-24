#pragma once

#include <string>
#include <vector>

namespace voltron::utility::timetravel {

/**
 * @brief Enable deterministic replay
 */
class DeterministicReplayHelper {
public:
    static DeterministicReplayHelper& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    DeterministicReplayHelper() = default;
    ~DeterministicReplayHelper() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::timetravel
