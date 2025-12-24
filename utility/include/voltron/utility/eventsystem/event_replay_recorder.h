#pragma once

#include <string>
#include <vector>

namespace voltron::utility::eventsystem {

/**
 * @brief Record events for replay
 */
class EventReplayRecorder {
public:
    static EventReplayRecorder& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    EventReplayRecorder() = default;
    ~EventReplayRecorder() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::eventsystem
