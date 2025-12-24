#pragma once

#include <string>
#include <vector>

namespace voltron::utility::embedded {

/**
 * @brief Measure interrupt response
 */
class InterruptLatencyTracker {
public:
    static InterruptLatencyTracker& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    InterruptLatencyTracker() = default;
    ~InterruptLatencyTracker() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::embedded
