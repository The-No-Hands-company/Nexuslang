#pragma once

#include <string>
#include <vector>

namespace voltron::utility::eventsystem {

/**
 * @brief Detect leaked subscriptions
 */
class SubscriberLeakDetector {
public:
    static SubscriberLeakDetector& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    SubscriberLeakDetector() = default;
    ~SubscriberLeakDetector() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::eventsystem
