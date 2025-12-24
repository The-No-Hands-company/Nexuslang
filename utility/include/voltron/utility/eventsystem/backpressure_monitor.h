#pragma once

#include <string>
#include <vector>

namespace voltron::utility::eventsystem {

/**
 * @brief Monitor queue backpressure
 */
class BackpressureMonitor {
public:
    static BackpressureMonitor& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    BackpressureMonitor() = default;
    ~BackpressureMonitor() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::eventsystem
