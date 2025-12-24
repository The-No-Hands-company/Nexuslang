#pragma once

#include <string>
#include <vector>

namespace voltron::utility::plugin {

/**
 * @brief Track dynamic library loading
 */
class DllLoadTracker {
public:
    static DllLoadTracker& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    DllLoadTracker() = default;
    ~DllLoadTracker() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::plugin
