#pragma once

#include <string>
#include <vector>

namespace voltron::utility::eventsystem {

/**
 * @brief Inspect queue depths
 */
class MessageQueueInspector {
public:
    static MessageQueueInspector& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    MessageQueueInspector() = default;
    ~MessageQueueInspector() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::eventsystem
