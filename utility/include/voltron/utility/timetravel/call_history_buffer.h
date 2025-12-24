#pragma once

#include <string>
#include <vector>

namespace voltron::utility::timetravel {

/**
 * @brief Ring buffer of recent calls
 */
class CallHistoryBuffer {
public:
    static CallHistoryBuffer& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    CallHistoryBuffer() = default;
    ~CallHistoryBuffer() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::timetravel
