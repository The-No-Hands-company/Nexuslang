#pragma once

#include <string>
#include <vector>

namespace voltron::utility::eventsystem {

/**
 * @brief Validate event ordering
 */
class EventOrderingValidator {
public:
    static EventOrderingValidator& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    EventOrderingValidator() = default;
    ~EventOrderingValidator() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::eventsystem
