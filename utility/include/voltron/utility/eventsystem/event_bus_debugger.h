#pragma once

#include <string>
#include <vector>

namespace voltron::utility::eventsystem {

/**
 * @brief Debug publish/subscribe systems
 */
class EventBusDebugger {
public:
    static EventBusDebugger& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    EventBusDebugger() = default;
    ~EventBusDebugger() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::eventsystem
