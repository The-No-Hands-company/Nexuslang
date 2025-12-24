#pragma once

#include <string>
#include <vector>

namespace voltron::utility::timetravel {

/**
 * @brief Interface for rr/gdb reverse
 */
class ReverseDebuggerInterface {
public:
    static ReverseDebuggerInterface& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    ReverseDebuggerInterface() = default;
    ~ReverseDebuggerInterface() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::timetravel
