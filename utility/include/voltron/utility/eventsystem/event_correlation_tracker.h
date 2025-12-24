#pragma once

#include <string>
#include <vector>

namespace voltron::utility::eventsystem {

/**
 * @brief Correlate related events
 */
class EventCorrelationTracker {
public:
    static EventCorrelationTracker& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    EventCorrelationTracker() = default;
    ~EventCorrelationTracker() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::eventsystem
