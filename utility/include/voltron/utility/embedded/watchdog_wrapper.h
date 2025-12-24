#pragma once

#include <string>
#include <vector>

namespace voltron::utility::embedded {

/**
 * @brief Hardware watchdog integration
 */
class WatchdogWrapper {
public:
    static WatchdogWrapper& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    WatchdogWrapper() = default;
    ~WatchdogWrapper() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::embedded
